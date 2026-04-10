let toastContainer = null;

function getContainer() {
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "toast-container";

    Object.assign(toastContainer.style, {
      position: "fixed",
      bottom: "20px",
      left: "calc(70px + 20px)", // avoids sidebar
      display: "flex",
      flexDirection: "column",
      gap: "10px",
      zIndex: "9999"
    });

    document.body.appendChild(toastContainer);
  }

  return toastContainer;
}

export function showToast(message) {
  const container = getContainer();

  const toast = document.createElement("div");
  toast.textContent = message;

  Object.assign(toast.style, {
    background: "#1f4e79",
    color: "white",
    padding: "12px 16px",
    borderRadius: "6px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
    minWidth: "220px",
    maxWidth: "320px",
    fontSize: "14px",

    opacity: "0",
    transform: "translateY(20px)",
    transition: "all 0.3s ease"
  });

  container.appendChild(toast);

  requestAnimationFrame(() => {
    toast.style.opacity = "1";
    toast.style.transform = "translateY(0)";
  });

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(20px)";

    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}