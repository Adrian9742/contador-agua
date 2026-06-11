const { app } = require('electron')
const { createWindow } = require('./window')
const { createTray } = require('./tray')
const reminders = require('./reminders')
const { registerHandlers } = require('./ipc')
const { loadState } = require('./store')

// Instância única
if (!app.requestSingleInstanceLock()) {
  app.quit()
  process.exit(0)
}

app.whenReady().then(() => {
  // 1. Carregar estado salvo antes de iniciar o timer (corrige race condition)
  const saved = loadState()
  if (saved) reminders.syncFromState(saved)

  // 2. Criar janela e bandeja
  const win = createWindow()
  createTray(win)

  // 3. Inicializar timer e reset de meia-noite com os valores corretos
  reminders.init(win)
  reminders.start()
  reminders.scheduleMidnightReset()

  // 4. Registrar handlers IPC
  registerHandlers()
})

app.on('window-all-closed', () => {
  // Não fecha — continua na bandeja
})

app.on('activate', () => {
  // macOS — não usado, mas boa prática manter
})

app.on('before-quit', () => {
  app.isQuitting = true
})
