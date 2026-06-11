const { Notification } = require('electron')

let win = null
let intervalMin = 30
let lastDrinkTime = Date.now()
let goalReached = false
let reminderTimer = null

function init(browserWindow) {
  win = browserWindow
}

function syncFromState(state) {
  if (state.intervalMin)   intervalMin   = state.intervalMin
  if (state.lastDrinkTime) lastDrinkTime = state.lastDrinkTime
  if (state.consumedMl !== undefined && state.goalMl !== undefined) {
    goalReached = state.consumedMl >= state.goalMl
  }
}

function start() {
  if (reminderTimer) clearInterval(reminderTimer)
  reminderTimer = setInterval(() => {
    if (goalReached) return
    const elapsed = (Date.now() - lastDrinkTime) / 1000
    if (elapsed >= intervalMin * 60) {
      fireReminder()
      lastDrinkTime = Date.now()
    }
  }, 10_000)
}

function fireReminder() {
  if (Notification.isSupported()) {
    new Notification({
      title: 'Hora de beber água! 💧',
      body: 'Você não bebeu água nos últimos minutos. Beba agora!',
    }).show()
  }
  if (win) win.webContents.send('reminder')
}

function scheduleMidnightReset() {
  const now = new Date()
  const next = new Date(now)
  next.setDate(next.getDate() + 1)
  next.setHours(0, 0, 5, 0)
  const msUntil = next - now

  setTimeout(() => {
    if (win) win.webContents.send('midnight-reset')
    scheduleMidnightReset()
  }, msUntil)
}

module.exports = { init, start, syncFromState, scheduleMidnightReset }
