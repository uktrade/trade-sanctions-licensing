const fs = require("fs");
const yaml = require("js-yaml");

function getConfig(configSource) {
  const config = _getData(configSource);
  console.log(`Loaded config with ${config.people.length} people`);
  return config;
}

function _getData(configSource) {
  const data = fs.readFileSync(configSource).toString();
  if (configSource.endsWith(".yaml") || configSource.endsWith(".yml"))
    return yaml.safeLoad(data);
  else return JSON.parse(data);
}

module.exports = { getConfig };
