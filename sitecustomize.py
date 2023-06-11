import sys
import os
import os.path
import subprocess

from bs4 import BeautifulSoup


STREMALIT_CDN_HOST = os.getenv('STREMALIT_CDN_HOST')
STREMALIT_CDN_PATH_PREFIX = os.getenv('STREMALIT_CDN_PATH_PREFIX', '')


def inplace_rewrite_resources(root: BeautifulSoup,
                              cdn_host: str, prefix: str = ''):
    for link in root.find_all('link'):
        if 'href' in link.attrs and link.attrs['href'].startswith('./'):
            link.attrs['href'] = f"//{cdn_host}{prefix}{link.attrs['href'].lstrip('.')}" # noqa
    for script in root.find_all('script'):
        if 'src' in script.attrs and script.attrs['src'].startswith('./'):
            script.attrs['src'] = f"//{cdn_host}{prefix}{script.attrs['src'].lstrip('.')}"  # noqa


def rewrite_content(content: str, cdn_host: str, prefix: str = ''):
    soup = BeautifulSoup(content, 'html.parser')
    inplace_rewrite_resources(soup, cdn_host, prefix)
    return soup.decode_contents()


def rewrite_cdn(path, cdn_host: str, prefix: str = ''):
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
            content = rewrite_content(content, cdn_host, prefix)
        with open(path, 'w') as f:
            f.write(content)


def rewrite_streamlit():
    import streamlit
    rewrite_cdn(
        f'{streamlit.__path__[0]}/static/index.html',
        STREMALIT_CDN_HOST,
        STREMALIT_CDN_PATH_PREFIX)


def load_streamlit_components():
    for p in [sys.prefix, os.path.join(os.getcwd(), 'src')]:
        if not os.path.exists(p):
            continue
        modules = subprocess.check_output(
            ["ag", "-l", r"declare_component\(", p], cwd=p).decode('utf-8')
        for i in set(modules.split('\n')):
            if 'site-packages/' in i:
                module_name = i.split('site-packages/')[1]
            else:
                module_name = i[len(p) + 1:]
            if module_name.endswith('/__init__.py'):
                module_name = module_name[:-len('/__init__.py')]
            elif module_name.endswith('.py'):
                module_name = module_name[:-len('.py')]
            module_name = module_name.replace('/', '.')
            try:
                __import__(module_name, {}, {})
            except BaseException:
                pass


def rewrite_streamlit_components():
    from streamlit.components.v1.components import ComponentRegistry
    registry = ComponentRegistry.instance()
    for component in registry._components.values():
        if not component.abspath:
            continue
        rewrite_cdn(os.path.join(component.abspath, 'index.html'),
                    STREMALIT_CDN_HOST,
                    f'{STREMALIT_CDN_PATH_PREFIX}/component/{component.name}')


# always force load all streamlit components
load_streamlit_components()


if STREMALIT_CDN_HOST and (not os.path.exists('/.streamlit_rewrite_done')):
    rewrite_streamlit()
    rewrite_streamlit_components()

    with open('/.streamlit_rewrite_done', 'w') as f:
        f.write('done')
