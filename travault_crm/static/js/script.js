document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector(".home-nav");
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const sections = document.querySelectorAll('section');


    const isHomePage = window.location.pathname === '/';  

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');

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
            } else if (targetId.startsWith('#') && !isHomePage) {
                e.preventDefault();
                window.location.href = '/' + targetId;  
            }
        });
    });

    // Combine scroll events
    window.onscroll = function() {
        if (isHomePage) {
            adjustNavbar();
            updateActiveLink();
        }
    };

    function adjustNavbar() {
        if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
            navbar.classList.add("navbar-scrolled");
        } else {
            navbar.classList.remove("navbar-scrolled");
        }
    }

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

    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.classList.remove('show');
            setTimeout(() => message.remove(), 150);
        }, 5000);
    });


    document.getElementById('supplierNameFilter').addEventListener('keyup', function () {
        var filterValue = this.value.toLowerCase();
        document.querySelectorAll('.supplier-item').forEach(function (item) {
            var supplierName = item.getAttribute('data-supplier-name').toLowerCase();
            item.style.display = supplierName.indexOf(filterValue) > -1 ? '' : 'none';
        });
    });

    // Filter suppliers by type
    document.getElementById('supplierTypeFilter').addEventListener('change', function () {
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

    // Adjust tabs
    function adjustTabs() {
        document.querySelectorAll('.nav-tabs').forEach(function (tabsContainer) {
            if (tabsContainer.scrollWidth > tabsContainer.clientWidth) {
                tabsContainer.classList.add('flex-nowrap', 'overflow-auto');
            } else {
                tabsContainer.classList.remove('flex-nowrap', 'overflow-auto');
            }
        });
    }

    adjustTabs();
    window.addEventListener('resize', adjustTabs);
});