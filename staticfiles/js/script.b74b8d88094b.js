/**
 * Initializes event listeners and adjusts the page layout on document load.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Select navbar and other elements
    const navbar = document.querySelector(".home-nav");
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const sections = document.querySelectorAll('section');

    // Check if the current page is the home page
    const isHomePage = window.location.pathname === '/';

    /**
     * Handles navigation link clicks for smooth scrolling or redirection.
     */
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');

            // Smooth scrolling for links on the home page
            if (targetId.startsWith('#') && isHomePage) {
                e.preventDefault();
                const targetSection = document.querySelector(targetId);
                if (targetSection) {
                    const navbarHeight = navbar.offsetHeight;
                    const targetPosition = targetSection.getBoundingClientRect().top + window.pageYOffset - navbarHeight;
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            } 
            // Redirect to home and scroll if not on home page
            else if (targetId.startsWith('#') && !isHomePage) {
                e.preventDefault();
                window.location.href = '/' + targetId;
            }
        });
    });

    /**
     * Combines scroll event handlers for navbar adjustment and link highlighting.
     */
    window.onscroll = function() {
        if (isHomePage) {
            adjustNavbar();
            updateActiveLink();
        }
    };

    /**
     * Adjusts the navbar style when scrolling past a certain point.
     */
    function adjustNavbar() {
        if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
            navbar.classList.add("navbar-scrolled");
        } else {
            navbar.classList.remove("navbar-scrolled");
        }
    }

    /**
     * Updates the active state of navbar links based on the current scroll position.
     */
    function updateActiveLink() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.scrollY >= sectionTop - sectionHeight / 3) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            if (link.getAttribute('href').startsWith('#')) {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.add('active');
                }
            }
        });
    }


    /**
     * Filters supplier items by name based on input from a search field.
     */
    document.addEventListener('DOMContentLoaded', function () {
        var supplierFilter = document.getElementById('supplierNameFilter');
        
        if (supplierFilter) {  // Only add event listener if element exists
            supplierFilter.addEventListener('keyup', function () {
                var filterValue = this.value.toLowerCase();
                document.querySelectorAll('.supplier-item').forEach(function (item) {
                    var supplierName = item.getAttribute('data-supplier-name').toLowerCase();
                    item.style.display = supplierName.indexOf(filterValue) > -1 ? '' : 'none';
                });
            });
        }
    });

    /**
     * Filters supplier items by type based on selection from a dropdown menu.
     */
    document.addEventListener('DOMContentLoaded', function () {
        var supplierTypeFilter = document.getElementById('supplierTypeFilter');
        
        if (supplierTypeFilter) {  // Only add event listener if the element exists
            supplierTypeFilter.addEventListener('change', function () {
                var filterValue = this.value;
                document.querySelectorAll('.supplier-item').forEach(function (item) {
                    var supplierType = item.getAttribute('data-supplier-type');
                    if (filterValue === "" || supplierType === filterValue) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        }
    });

    /**
     * Adjusts the appearance of tabs if they overflow their container.
     */
    function adjustTabs() {
        document.querySelectorAll('.nav-tabs').forEach(function (tabsContainer) {
            if (tabsContainer.scrollWidth > tabsContainer.clientWidth) {
                tabsContainer.classList.add('flex-nowrap', 'overflow-auto');
            } else {
                tabsContainer.classList.remove('flex-nowrap', 'overflow-auto');
            }
        });
    }

    // Initial adjustment and listener for resizing
    adjustTabs();
    window.addEventListener('resize', adjustTabs);
});