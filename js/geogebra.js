

(function () {
  const Vue = window.Vue
  const { ref, onMounted, onBeforeUnmount, nextTick } = Vue

  function useGeoGebra() {
    const ggbApplet = ref(null)
    const ggbElement = ref(null)
    const show = ref(true)
    const enable3D = ref(false)

    let resizeObserver = null
    let currentAppletWrapper = null

    function buildAppletConfig(is3D) {
      return {
        appName: is3D ? '3d' : 'classic',
        showToolBar: true,
        showAlgebraInput: true,
        showMenuBar: true,
        filename: '',
        borderColor: 'transparent',
        showFullscreenButton: true,
        showResetIcon: true,
        enableRightClick: true,
        disableAutoScale: true,
        width: 400,
        height: 300,
        appletOnLoad: (api) => {
          ggbApplet.value = api
          resizeGGB()
        }
      }
    }

    function resizeGGB() {
      if (!ggbApplet.value || !ggbElement.value) return
      ggbElement.value.style.width = ''
      ggbElement.value.style.height = ''
      requestAnimationFrame(() => {
        if (!ggbElement.value) return
        const rect = ggbElement.value.getBoundingClientRect()
        ggbApplet.value.setWidth(Math.round(rect.width))
        ggbApplet.value.setHeight(Math.round(rect.height))
      })
    }

    function initGGBApplet(is3D) {
      if (!window.GGBApplet) {
        console.error('GGBApplet not found. Is deployggb.js loaded?')
        return null
      }
      const config = buildAppletConfig(is3D)
      const wrapper = new window.GGBApplet(config)
      wrapper.inject('ggb-element', 'html5')
      currentAppletWrapper = wrapper
      return wrapper
    }

    function rebuildApplet(is3D) {
      ggbApplet.value = null
      try {
        if (currentAppletWrapper) {
          currentAppletWrapper.removeExistingApplet('ggb-element', false)
        }
      } catch (e) {
        console.warn('removeExistingApplet failed:', e)
      }
      const container = document.getElementById('ggb-element')
      if (container) container.innerHTML = ''
      requestAnimationFrame(() => {
        initGGBApplet(is3D)
        requestAnimationFrame(() => resizeGGB())
      })
    }

    function switchPerspective(is3D) {
      if (!ggbApplet.value) return
      try {
        ggbApplet.value.evalCommand(is3D ? 'SetPerspective("AGT")' : 'SetPerspective("AG")')
        enable3D.value = is3D
      } catch (e) {
        console.warn('SetPerspective failed, fallback to rebuild:', e)
        setEnable3D(is3D)
      }
    }

    function setEnable3D(value) {
      enable3D.value = value
      rebuildApplet(value)
    }

    function resetApplet() {
      rebuildApplet(enable3D.value)
    }

    function toggleToolBar() {
      if (!ggbApplet.value) return
      show.value = !show.value
      ggbApplet.value.showToolBar(show.value)
      ggbApplet.value.showAlgebraInput(show.value)
      ggbApplet.value.showMenuBar(show.value)
      ggbApplet.value.enableRightClick(show.value)
    }

    // 在组件 setup 里注册生命周期
    // Vue global build 里 onMounted 等必须在 setup 同步调用
    onMounted(() => {
      // 如果 GeoGebra deployggb.js 还没加载完（defer），等 window.GGBApplet 出现再初始化
      const tryInit = () => {
        if (window.GGBApplet) {
          initGGBApplet(false)
          if (ggbElement.value) {
            resizeObserver = new ResizeObserver(resizeGGB)
            resizeObserver.observe(ggbElement.value)
          }
          window.addEventListener('resize', resizeGGB)
        } else {
          setTimeout(tryInit, 200)
        }
      }
      tryInit()
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', resizeGGB)
      if (resizeObserver && ggbElement.value) {
        resizeObserver.unobserve(ggbElement.value)
        resizeObserver.disconnect()
      }
    })

    return {
      ggbApplet,
      ggbElement,
      show,
      enable3D,
      toggleToolBar,
      setEnable3D,
      resetApplet,
      switchPerspective
    }
  }

  window.useGeoGebra = useGeoGebra
})()