
    const sidebar = document.getElementById('sidebar');
    const sidebarTitle = document.getElementById('sidebar-title');
    const links = document.querySelectorAll('.link-text');
    const toggleSidebar = document.getElementById('toggleSidebar');

    toggleSidebar.addEventListener('click', function () {
        if (sidebar.style.width === '250px') {
            sidebar.style.width = '80px';
            sidebarTitle.style.display = 'none';
            links.forEach(link => link.style.display = 'none');
        } else {
            sidebar.style.width = '250px';
            sidebarTitle.style.display = 'block';
            links.forEach(link => link.style.display = 'inline');
        }
    });
