// PhoneGuard phone-web: thu thập telemetry Android và gửi tới FastAPI backend.

const state = {
  timerId: null,
  batteryManager: null,
  batterySupported: false,
  motionSupported: false,
  motionPermissionAsked: false,
  latestMotion: { acc_x: null, acc_y: null, acc_z: null },
};

const els = {
  backendUrl: document.getElementById("backendUrl"),
  deviceId: document.getElementById("deviceId"),
  startBtn: document.getElementById("startBtn"),
  stopBtn: document.getElementById("stopBtn"),
  sendStatus: document.getElementById("sendStatus"),
  statusBox: document.getElementById("statusBox"),
  batteryWarning: document.getElementById("batteryWarning"),
  motionWarning: document.getElementById("motionWarning"),
  batteryText: document.getElementById("batteryText"),
  chargingText: document.getElementById("chargingText"),
  motionText: document.getElementById("motionText"),
  networkText: document.getElementById("networkText"),
  payloadView: document.getElementById("payloadView"),
};

function setStatus(text, isError = false) {
  // Cập nhật trạng thái gửi để người dùng biết request mới nhất thành công hay thất bại.
  els.sendStatus.textContent = text;
  els.statusBox.classList.toggle("error", isError);
  console.log("[DEBUG] Status:", text);
}

async function initBattery() {
  // Battery API không còn được hỗ trợ rộng rãi, nên luôn có fallback rõ ràng.
  if (!("getBattery" in navigator)) {
    state.batterySupported = false;
    els.batteryWarning.classList.remove("hidden");
    console.log("[DEBUG] Battery API khong duoc ho tro");
    return;
  }

  try {
    state.batteryManager = await navigator.getBattery();
    state.batterySupported = true;
    els.batteryWarning.classList.add("hidden");
    console.log("[DEBUG] Battery API ready", {
      level: state.batteryManager.level,
      charging: state.batteryManager.charging,
    });
  } catch (error) {
    state.batterySupported = false;
    els.batteryWarning.classList.remove("hidden");
    console.log("[DEBUG] Loi Battery API", error);
  }
}

async function requestMotionPermissionIfNeeded() {
  // Một số trình duyệt yêu cầu quyền cảm biến sau thao tác bấm nút của người dùng.
  if (!window.DeviceMotionEvent) {
    state.motionSupported = false;
    els.motionWarning.classList.remove("hidden");
    console.log("[DEBUG] DeviceMotionEvent khong duoc ho tro");
    return;
  }

  if (typeof DeviceMotionEvent.requestPermission === "function" && !state.motionPermissionAsked) {
    state.motionPermissionAsked = true;
    try {
      const permission = await DeviceMotionEvent.requestPermission();
      if (permission !== "granted") {
        state.motionSupported = false;
        els.motionWarning.classList.remove("hidden");
        console.log("[DEBUG] DeviceMotion permission bi tu choi");
        return;
      }
    } catch (error) {
      state.motionSupported = false;
      els.motionWarning.classList.remove("hidden");
      console.log("[DEBUG] Loi xin quyen DeviceMotion", error);
      return;
    }
  }

  state.motionSupported = true;
  els.motionWarning.classList.add("hidden");
  console.log("[DEBUG] DeviceMotion ready");
}

function attachMotionListener() {
  // Lắng nghe gia tốc; nếu trình duyệt không trả dữ liệu thì fallback vẫn là null.
  window.addEventListener(
    "devicemotion",
    (event) => {
      const acc = event.accelerationIncludingGravity || event.acceleration;
      if (!acc) return;
      state.latestMotion = {
        acc_x: Number.isFinite(acc.x) ? Number(acc.x.toFixed(3)) : null,
        acc_y: Number.isFinite(acc.y) ? Number(acc.y.toFixed(3)) : null,
        acc_z: Number.isFinite(acc.z) ? Number(acc.z.toFixed(3)) : null,
      };
      state.motionSupported = true;
      els.motionWarning.classList.add("hidden");
    },
    true,
  );
}

function getBatteryTelemetry() {
  if (!state.batterySupported || !state.batteryManager) {
    return { battery_level: 50, charging: false };
  }
  return {
    battery_level: Math.round(state.batteryManager.level * 1000) / 10,
    charging: Boolean(state.batteryManager.charging),
  };
}

function getNetworkType() {
  // Theo yêu cầu, dùng navigator.onLine để phân loại kết nối cơ bản.
  return navigator.onLine ? "online" : "offline";
}

function buildPayload() {
  const battery = getBatteryTelemetry();
  return {
    device_id: els.deviceId.value.trim() || "android-phone-001",
    timestamp: new Date().toISOString(),
    battery_level: battery.battery_level,
    charging: battery.charging,
    acc_x: state.motionSupported ? state.latestMotion.acc_x : null,
    acc_y: state.motionSupported ? state.latestMotion.acc_y : null,
    acc_z: state.motionSupported ? state.latestMotion.acc_z : null,
    light_lux: null,
    network_type: getNetworkType(),
  };
}

function updatePayloadUi(payload) {
  els.batteryText.textContent = `${payload.battery_level}%`;
  els.chargingText.textContent = payload.charging ? "true" : "false";
  els.motionText.textContent =
    payload.acc_x === null || payload.acc_y === null || payload.acc_z === null
      ? "fallback: null"
      : `${payload.acc_x}, ${payload.acc_y}, ${payload.acc_z}`;
  els.networkText.textContent = payload.network_type;
  els.payloadView.textContent = JSON.stringify(payload, null, 2);
}

async function sendTelemetry() {
  const payload = buildPayload();
  updatePayloadUi(payload);

  const baseUrl = els.backendUrl.value.trim().replace(/\/$/, "");
  const url = `${baseUrl}/telemetry`;
  console.log("[DEBUG] Gui telemetry", { url, payload });
  setStatus("Sending...");

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`HTTP ${response.status}: ${body}`);
    }

    const result = await response.json();
    console.log("[DEBUG] Gui thanh cong", result);
    setStatus(`Success ${new Date().toLocaleTimeString()}`);
  } catch (error) {
    console.log("[DEBUG] Gui that bai", error);
    setStatus(`Failed: ${error.message}`, true);
  }
}

async function startSending() {
  els.startBtn.disabled = true;
  els.stopBtn.disabled = false;
  setStatus("Starting...");

  await initBattery();
  await requestMotionPermissionIfNeeded();
  attachMotionListener();

  if (!state.motionSupported) {
    els.motionWarning.classList.remove("hidden");
  }

  await sendTelemetry();
  state.timerId = window.setInterval(sendTelemetry, 3000);
  console.log("[DEBUG] Bat dau gui telemetry moi 3 giay");
}

function stopSending() {
  if (state.timerId) {
    window.clearInterval(state.timerId);
    state.timerId = null;
  }
  els.startBtn.disabled = false;
  els.stopBtn.disabled = true;
  setStatus("Stopped");
  console.log("[DEBUG] Dung gui telemetry");
}

els.startBtn.addEventListener("click", startSending);
els.stopBtn.addEventListener("click", stopSending);

window.addEventListener("online", () => {
  console.log("[DEBUG] Network online");
});

window.addEventListener("offline", () => {
  console.log("[DEBUG] Network offline");
});

setStatus("Idle");
