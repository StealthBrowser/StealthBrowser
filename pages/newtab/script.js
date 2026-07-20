document.getElementById('search').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') {
    const query = this.value.trim();
    if (query) {
      if (/^https?:\/\//.test(query)) {
        window.location.href = query;
      } else if (/^[\w-]+(\.[\w-]+)+/.test(query)) {
        window.location.href = 'https://' + query;
      } else {
        window.location.href = 'https://duckduckgo.com/?q=' + encodeURIComponent(query);
      }
    }
  }
});
