document.querySelectorAll('input[type="checkbox"]').forEach(function(el) {
  el.addEventListener('change', function() {
    const config = {};
    document.querySelectorAll('input[type="checkbox"]').forEach(function(cb) {
      config[cb.id] = cb.checked;
    });
    console.log('Settings updated:', config);
  });
});
