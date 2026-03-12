export function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-2 right-2 px-6 py-3 text-sm rounded-sm shadow-lg text-gray-600 ${type === 'success' ? 'bg-green-200' : 'bg-red-500'
        }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}