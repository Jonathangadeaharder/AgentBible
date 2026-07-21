(function() {
  var results = [];
  var seen = {};
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  var itemInfos = [];
  var node;
  while (node = walker.nextNode()) {
    if (node.textContent && node.textContent.trim() === 'Item Info') {
      itemInfos.push(node.parentElement);
    }
  }
  itemInfos.forEach(function(container) {
    var card = container;
    for (var i = 0; i < 5; i++) {
      card = card.parentElement;
      if (!card) break;
      var text = card.textContent;
      if (text && text.length > 30 && text.length < 500) {
        var priceMatch = text.match(/(\d+[,.]\d+)\s*\u20ac/);
        var lines = text.split(/\n/).map(function(l) { return l.trim(); })
          .filter(function(l) {
            return l && l !== 'Item Info' &&
              !l.match(/^\d+[,.]\d+\s*\u20ac?$/) && l.length > 3;
          });
        var name = lines[0] || '';
        name = name.replace(/^(.+?)\1+/, '$1');
        var price = priceMatch ? priceMatch[1].replace('.', ',') + '\u20ac' : '';
        var key = name + '|' + price;
        if (name.length > 3 && price && !seen[key]) {
          seen[key] = true;
          results.push({ name: name.slice(0, 80), price: price });
        }
        break;
      }
    }
  });
  return JSON.stringify(results);
})()
