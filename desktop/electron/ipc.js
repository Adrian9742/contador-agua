const { ipcMain, Notification } = require('electron')
const { loadState, saveState } = require('./store')
const reminders = require('./reminders')

function registerHandlers() {
  ipcMain.handle('load-state', () => loadState())

  ipcMain.handle('save-state', (_, data) => {
    saveState(data)
    reminders.syncFromState(data)
  })

  ipcMain.handle('notify-goal', () => {
    if (Notification.isSupported()) {
      new Notification({
        title: 'Meta diária atingida! 🎉',
        body: 'Parabéns! Você bateu sua meta de hidratação hoje!',
      }).show()
    }
  })
}

module.exports = { registerHandlers }
