// Console utility for digilawyer scraping
const https = require('https');

function fetch(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

async function scrapeCases() {
  const html = await fetch('https://digilawyer.com/cases');
  console.log('Fetched cases page');
  return html;
}

module.exports = { scrapeCases };
