module.exports = {
  devServer: {
    port: 8000,
    proxy: {
      '/api-v1': {
        target: 'http://localhost:9030', // Replace with your backend server
        ws: true,  // Enable WebSocket proxy for your API
        changeOrigin: true
      }
    }
  }
}
