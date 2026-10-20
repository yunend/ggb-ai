
(function () {
  // ===== 颜色表 =====
  const NAMED_COLORS = {
    black: [0, 0, 0], blue: [0, 0, 255], cyan: [0, 255, 255],
    gray: [128, 128, 128], green: [0, 128, 0], lime: [0, 255, 0],
    magenta: [255, 0, 255], maroon: [128, 0, 0], navy: [0, 0, 128],
    olive: [128, 128, 0], purple: [128, 0, 128], red: [255, 0, 0],
    silver: [192, 192, 192], teal: [0, 128, 128], white: [255, 255, 255],
    yellow: [255, 255, 0],
    lightgray: [200, 200, 200], lightgrey: [200, 200, 200],
    darkgray: [64, 64, 64], darkgrey: [64, 64, 64],
    gainsboro: [220, 220, 220],
    orange: [255, 165, 0], darkorange: [255, 140, 0],
    pink: [255, 192, 203], hotpink: [255, 105, 180], deeppink: [255, 20, 147],
    brown: [165, 42, 42], saddlebrown: [139, 69, 19], sienna: [160, 82, 45],
    chocolate: [210, 105, 30],
    gold: [255, 215, 0], khaki: [240, 230, 140], beige: [245, 245, 220],
    coral: [255, 127, 80], tomato: [255, 99, 71], salmon: [250, 128, 114],
    violet: [238, 130, 238], plum: [221, 160, 221], orchid: [218, 112, 214],
    indigo: [75, 0, 130], bisque: [255, 228, 196], wheat: [245, 222, 179],
    tan: [210, 180, 140], azure: [240, 255, 255], ivory: [255, 255, 240],
    lavender: [230, 230, 250]
  }

  // ===== 命令 → JS API 映射 =====
  const CMD_TO_JS_API = {
    showlabel: 'setLabelVisible', showlabels: 'setLabelVisible',
    hidelabel: 'setLabelVisible', hidelabels: 'setLabelVisible',
    setlabelmode: 'setLabelStyle', setlabelstyle: 'setLabelStyle',
    setpointstyle: 'setPointStyle', setpointsize: 'setPointSize',
    setlinestyle: 'setLineStyle', setlinewidth: 'setLineThickness',
    setlinethickness: 'setLineThickness', setfilling: 'setFilling',
    setlayer: 'setLayer', settrace: 'setTrace', hidetrace: 'setTrace',
    setcaption: 'setCaption', setcolor: 'setColor',
    deleteobject: 'deleteObject', removeobject: 'deleteObject',
    delete: 'deleteObject', reset: 'reset'
  }

  // ===== 参数解析 =====
  function parseArgs(argStr) {
    const args = []
    if (!argStr.trim()) return args
    let current = ''
    let inQuote = null
    let depth = 0
    for (let i = 0; i < argStr.length; i++) {
      const ch = argStr[i]
      if (inQuote) {
        if (ch === inQuote) inQuote = null
        else current += ch
      } else if (ch === '"' || ch === "'") {
        inQuote = ch
      } else if (ch === '(') {
        depth++; current += ch
      } else if (ch === ')') {
        depth--; current += ch
      } else if (ch === ',' && depth === 0) {
        args.push(convertArg(current.trim()))
        current = ''
      } else {
        current += ch
      }
    }
    if (current.trim()) args.push(convertArg(current.trim()))
    return args
  }

  function convertArg(s) {
    if (s.toLowerCase() === 'true') return true
    if (s.toLowerCase() === 'false') return false
    const num = Number(s)
    if (!Number.isNaN(num) && s !== '') return num
    const pointMatch = s.match(/^\(([^)]+)\)$/)
    if (pointMatch) return parseArgs(pointMatch[1])
    return s
  }

  // ===== 颜色参数解析 =====
  function parseColorArgs(argStr) {
    const args = parseArgs(argStr)
    console.log('[parseColorArgs] argStr:', JSON.stringify(argStr), '→ args:', args)
    if (args.length < 2) return { ok: false, objName: '', msg: 'SetColor 需要至少 2 个参数：对象名 + 颜色（实际收到: ' + JSON.stringify(argStr) + ' → ' + JSON.stringify(args) + '）' }
    const objName = String(args[0])
    const colorArg = args[1]

    if (typeof colorArg === 'string') {
      const key = colorArg.toLowerCase()
      if (NAMED_COLORS[key]) return { ok: true, objName, rgb: NAMED_COLORS[key] }
      return { ok: false, objName, msg: '未识别的命名颜色 "' + colorArg + '"，支持: ' + Object.keys(NAMED_COLORS).join(', ') }
    }

    if (Array.isArray(colorArg) && colorArg.length === 3) {
      const rgb = colorArg.map(function (v) {
        const n = Number(v)
        if (n <= 1 && n >= 0) return Math.round(n * 255)
        return Math.round(n)
      })
      return { ok: true, objName, rgb: rgb }
    }

    if (args.length === 4) {
      const rgb = args.slice(1, 4).map(function (v) {
        const n = Number(v)
        if (n <= 1 && n >= 0) return Math.round(n * 255)
        return Math.round(n)
      })
      return { ok: true, objName, rgb: rgb }
    }

    return { ok: false, objName, msg: '无法解析颜色参数（支持命名颜色如 red，或 (r,g,b) 数组）' }
  }

  // ===== JS API 智能查找 =====
  function findMethod(applet, preferred, keywords) {
    if (typeof applet[preferred] === 'function') return preferred
    const allKeys = Object.getOwnPropertyNames(applet).concat(Object.keys(applet))
    const methods = allKeys.filter(function (k) { return typeof applet[k] === 'function' })
    for (const kw of keywords) {
      const exact = methods.find(function (m) { return m.toLowerCase() === kw.toLowerCase() })
      if (exact) return exact
    }
    for (const kw of keywords) {
      const contains = methods.find(function (m) { return m.toLowerCase().includes(kw.toLowerCase()) })
      if (contains) return contains
    }
    return null
  }

  function callJsApi(applet, line) {
    const m = line.match(/^(\s*[A-Za-z]+)\s*(?:\((.*)\))?\s*$/)
    if (!m) return { ok: false, msg: '无法解析命令格式' }
    const alias = m[1].trim().toLowerCase()
    const preferredMethod = CMD_TO_JS_API[alias]
    if (!preferredMethod) return { ok: false, msg: '未匹配到 JS API: ' + alias }
    const keywords = [preferredMethod.toLowerCase()]
    const method = findMethod(applet, preferredMethod, keywords)
    if (!method) {
      return { ok: false, msg: 'ggbApplet 上找不到方法（尝试了 ' + preferredMethod + ' 及关键词 ' + keywords.join('/') + '）' }
    }
    let args = parseArgs(m[2] || '')
    const wantsHidden = alias.startsWith('hide')
    if (alias === 'hidelabel' || alias === 'hidelabels') {
      args = [args[0], false]
    }
    if (alias === 'hideobject' || alias === 'hide') {
      args = [args[0], false]
    }
    try {
      applet[method].apply(applet, args)
      const hint = method !== preferredMethod ? '(自动匹配 ' + method + ')' : ''
      return { ok: true, msg: method + '(' + args.map(function (a) { return JSON.stringify(a) }).join(', ') + ') ' + hint }
    } catch (e) {
      return { ok: false, msg: e.message || String(e) }
    }
  }

  // 挂到 window
  window.CMD_TO_JS_API = CMD_TO_JS_API
  window.parseColorArgs = parseColorArgs
  window.callJsApi = callJsApi
})()