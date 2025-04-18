/**
 * Recommendations JavaScript for BookSage
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // Handle recommendation filtering
    const filterButtons = document.querySelectorAll('.filter-btn');
    const recommendationItems = document.querySelectorAll('.recommendation-item');
    
    if (filterButtons.length > 0 && recommendationItems.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Get filter value
                const filterValue = this.getAttribute('data-filter');
                
                // Filter recommendations
                recommendationItems.forEach(item => {
                    if (filterValue === 'all' || item.classList.contains(filterValue)) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }
    
    // Handle recommendation sorting
    const sortSelect = document.getElementById('sortRecommendations');
    const recommendationsContainer = document.querySelector('.recommendations-container');
    
    if (sortSelect && recommendationsContainer && recommendationItems.length > 0) {
        sortSelect.addEventListener('change', function() {
            const sortValue = this.value;
            const items = Array.from(recommendationItems);
            
            // Sort items based on selected option
            items.sort((a, b) => {
                if (sortValue === 'score-high') {
                    return parseFloat(b.getAttribute('data-score')) - parseFloat(a.getAttribute('data-score'));
                } else if (sortValue === 'score-low') {
                    return parseFloat(a.getAttribute('data-score')) - parseFloat(b.getAttribute('data-score'));
                } else if (sortValue === 'rating-high') {
                    return parseFloat(b.getAttribute('data-rating')) - parseFloat(a.getAttribute('data-rating'));
                } else if (sortValue === 'rating-low') {
                    return parseFloat(a.getAttribute('data-rating')) - parseFloat(b.getAttribute('data-rating'));
                } else if (sortValue === 'title-az') {
                    return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
                } else if (sortValue === 'title-za') {
                    return b.getAttribute('data-title').localeCompare(a.getAttribute('data-title'));
                }
                return 0;
            });
            
            // Reappend sorted items
            items.forEach(item => {
                recommendationsContainer.appendChild(item);
            });
        });
    }
    
    // Handle recommendation refresh
    const refreshButton = document.getElementById('refreshRecommendations');
    
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            // Show loading state
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
            this.disabled = true;
            
            // Make AJAX request to refresh recommendations
            fetch('/refresh-recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload the page to show new recommendations
                    window.location.reload();
                } else {
                    // Show error message
                    alert('Failed to refresh recommendations. Please try again.');
                    
                    // Reset button
                    this.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Recommendations';
                    this.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Show error message
                alert('An error occurred. Please try again later.');
                
                // Reset button
                this.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Recommendations';
                this.disabled = false;
            });
        });
    }
    
    // Handle lazy loading of recommendation images
    const recommendationImages = document.querySelectorAll('.recommendation-image');
    
    if (recommendationImages.length > 0) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    
                    if (src) {
                        img.src = src;
                        img.removeAttribute('data-src');
                    }
                    
                    observer.unobserve(img);
                }
            });
        });
        
        recommendationImages.forEach(img => {
            imageObserver.observe(img);
        });
    }
});
