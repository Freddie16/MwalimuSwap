// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('main.js loaded and DOM is ready.');

    // Example: Add active class to current sidebar link
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a');

    sidebarLinks.forEach(link => {
        // Check if the link's href matches the current path
        // Adjust logic if your URLs are more complex (e.g., include query params)
        if (link.getAttribute('href') === currentPath ||
            (currentPath.startsWith('/users/') && link.getAttribute('href') === '/users/profile/') ||
            (currentPath.startsWith('/swaps/') && link.getAttribute('href') === '/swaps/dashboard/')) {
            link.classList.add('active');
        }
    });

    // You can add more global JavaScript functionality here,
    // e.g., handling dropdowns, modals, etc.
    
    // Example: Simple user profile dropdown (conceptual)
    const userProfileToggle = document.querySelector('.top-nav .user-profile');
    if (userProfileToggle) {
        userProfileToggle.addEventListener('click', function() {
            // Implement dropdown toggle logic here
            console.log('User profile clicked!');
            // For a real dropdown, you'd toggle a class on a hidden menu
            // e.g., document.getElementById('user-dropdown-menu').classList.toggle('hidden');
        });
    }
});
