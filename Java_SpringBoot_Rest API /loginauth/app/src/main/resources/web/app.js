console.log("Auth demo page loaded");

const logoutButton = document.getElementById("logout");
logoutButton?.addEventListener("click", async () => {
    const response = await fetch("/api/logout", {
        method: "POST",
        credentials: "include"
    });

    if (response.ok) {
        window.location.replace("/login");
        return;
    }

    console.error("로그아웃 실패:", response.status);
});