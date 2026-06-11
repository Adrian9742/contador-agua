const { app } = require('electron')
const path = require('path')
const fs = require('fs')

const statePath = path.join(app.getPath('userData'), 'state.json')

function loadState() {
  try {
    if (fs.existsSync(statePath)) {
      return JSON.parse(fs.readFileSync(statePath, 'utf-8'))
    }
  } catch {}
  return null
}

function saveState(data) {
  try {
    fs.writeFileSync(statePath, JSON.stringify(data), 'utf-8')
  } catch {}
}

module.exports = { loadState, saveState }
