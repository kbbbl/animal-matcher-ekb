document.addEventListener('DOMContentLoaded', function() {
    console.log('Animal Matcher EKB loaded successfully');

    const animalCards = document.querySelectorAll('.animal-card');
    animalCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });

    const filterForm = document.querySelector('form[method="get"]');
    if (filterForm) {
        const inputs = filterForm.querySelectorAll('select, input[type="text"]');
        inputs.forEach(input => {
            if (input.value) {
                input.classList.add('border-primary');
            }
        });
    }

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});