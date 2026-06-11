const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  platform: 'electron',

  // Estado persistente
  loadState:  ()       => ipcRenderer.invoke('load-state'),
  saveState:  (data)   => ipcRenderer.invoke('save-state', data),

  // Notificação de meta atingida (dispara toast nativo)
  notifyGoal: ()       => ipcRenderer.invoke('notify-goal'),

  // Eventos do processo principal → renderer
  onReminder:      (cb) => ipcRenderer.on('reminder',      () => cb()),
  onMidnightReset: (cb) => ipcRenderer.on('midnight-reset', () => cb()),
})
