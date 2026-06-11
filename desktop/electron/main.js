const { app, BrowserWindow, Tray, Menu, ipcMain, Notification, shell } = require('electron')
const path = require('path')
const fs = require('fs')

const isDev = process.env.NODE_ENV === 'development'

let win = null
let tray = null

// ── Persistência ──────────────────────────────────────────────────────────────
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

// ── Janela principal ──────────────────────────────────────────────────────────
function createWindow() {
  const iconPath = path.join(__dirname, '..', 'assets', 'icon.ico')

  win = new BrowserWindow({
    width: 460,
    height: 870,
    minWidth: 460,
    minHeight: 700,
    resizable: false,
    maximizable: false,
    title: 'Contador de Água',
    icon: fs.existsSync(iconPath) ? iconPath : undefined,
    backgroundColor: '#0d1424',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (isDev) {
    win.loadURL('http://localhost:3000')
    win.webContents.openDevTools({ mode: 'detach' })
  } else {
    win.loadFile(path.join(__dirname, '..', 'out', 'index.html'))
  }

  // Minimiza para tray em vez de fechar
  win.on('close', (e) => {
    if (!app.isQuitting) {
      e.preventDefault()
      win.hide()
    }
  })
}

// ── Bandeja do sistema ────────────────────────────────────────────────────────
function createTray() {
  const iconPath = path.join(__dirname, '..', 'assets', 'icon.ico')
  const fallbackIcon = path.join(__dirname, '..', 'public', 'icon.svg')
  const icon = fs.existsSync(iconPath) ? iconPath : fallbackIcon

  try {
    tray = new Tray(icon)
  } catch {
    return
  }

  const updateMenu = () => {
    const menu = Menu.buildFromTemplate([
      {
        label: 'Abrir Contador de Água',
        click: () => { win.show(); win.focus() },
      },
      { type: 'separator' },
      {
        label: 'Sair',
        click: () => { app.isQuitting = true; app.quit() },
      },
    ])
    tray.setContextMenu(menu)
  }

  tray.setToolTip('Contador de Água')
  updateMenu()
  tray.on('click', () => { win.show(); win.focus() })
}

// ── Timer de lembretes (roda no processo principal) ───────────────────────────
let lastDrinkTime = Date.now()
let intervalMin = 30
let goalReached = false
let reminderTimer = null

function startReminderTimer() {
  if (reminderTimer) clearInterval(reminderTimer)

  reminderTimer = setInterval(() => {
    if (goalReached) return
    const elapsed = (Date.now() - lastDrinkTime) / 1000
    if (elapsed >= intervalMin * 60) {
      fireReminder()
      lastDrinkTime = Date.now()
    }
  }, 10_000) // verifica a cada 10s
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

// ── Auto-reset à meia-noite ───────────────────────────────────────────────────
function scheduleMidnightReset() {
  const now = new Date()
  const next = new Date(now)
  next.setDate(next.getDate() + 1)
  next.setHours(0, 0, 5, 0) // 00:00:05 do próximo dia
  const msUntil = next - now

  setTimeout(() => {
    if (win) win.webContents.send('midnight-reset')
    scheduleMidnightReset() // agenda o próximo
  }, msUntil)
}

// ── IPC handlers ──────────────────────────────────────────────────────────────
ipcMain.handle('load-state', () => loadState())

ipcMain.handle('save-state', (_, data) => {
  saveState(data)
  if (data.intervalMin)    intervalMin    = data.intervalMin
  if (data.lastDrinkTime)  lastDrinkTime  = data.lastDrinkTime
  if (data.consumedMl !== undefined && data.goalMl !== undefined) {
    goalReached = data.consumedMl >= data.goalMl
  }
})

ipcMain.handle('notify-goal', () => {
  if (Notification.isSupported()) {
    new Notification({
      title: 'Meta diária atingida! 🎉',
      body: 'Parabéns! Você bateu sua meta de hidratação hoje!',
    }).show()
  }
})

// ── Inicialização ─────────────────────────────────────────────────────────────
app.whenReady().then(() => {
  createWindow()
  createTray()
  startReminderTimer()
  scheduleMidnightReset()

  // Restaura params do timer com base no estado salvo
  const saved = loadState()
  if (saved) {
    intervalMin   = saved.intervalMin   ?? 30
    lastDrinkTime = saved.lastDrinkTime ?? Date.now()
    goalReached   = (saved.consumedMl ?? 0) >= (saved.goalMl ?? 2000)
  }
})

app.on('window-all-closed', () => {
  // Não fecha — continua na bandeja
})

app.on('activate', () => {
  if (win) win.show()
})

app.on('before-quit', () => {
  app.isQuitting = true
})
