# streamlit-cdn

- Preload all Streamlit components in advance to ensure that static files are displayed properly in multiple instances. 
- Support rewriting all Streamlit components and Streamlit's own static files to CDN in container environments.

## Chunked Resources

Re-Compile package frontend with automatic `publicPath` detection enabled.
```python
module.exports = {
  output: {
    publicPath: 'auto',
  },
};
```
For streamlit, check https://github.com/pragmatic-streamlit/streamlit

## Dependencies

- beautifulsoup4 (Pypi)
- silversearcher-ag (System)