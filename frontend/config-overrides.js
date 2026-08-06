const { override, addBabelPlugins, babelInclude } = require('customize-cra');

module.exports = override(
  addBabelPlugins('@babel/plugin-proposal-optional-chaining'),
  babelInclude([
    // Include paths if needed
  ])
);
