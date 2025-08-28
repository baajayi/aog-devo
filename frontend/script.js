// Use relative URLs for production deployment
const API_BASE_URL = window.location.origin;

class DevotionalApp {
    constructor() {
        this.initializeEventListeners();
        this.loadSuggestedTopics();
    }

    initializeEventListeners() {
        const form = document.getElementById('devotionalForm');
        const generateAnotherBtn = document.getElementById('generateAnotherBtn');
        const printBtn = document.getElementById('printBtn');

        form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        generateAnotherBtn.addEventListener('click', () => this.resetForm());
        printBtn.addEventListener('click', () => this.printDevotional());
    }

    async loadSuggestedTopics() {
        try {
            const response = await fetch(`${API_BASE_URL}/topics`);
            const data = await response.json();
            this.renderTopicSuggestions(data.topics);
        } catch (error) {
            console.error('Error loading topics:', error);
            // Fallback topics
            const fallbackTopics = [
                'Faith and Trust', 'Love and Kindness', 'Prayer and Worship',
                'Forgiveness', 'Patience', 'Gratitude', 'Courage'
            ];
            this.renderTopicSuggestions(fallbackTopics);
        }
    }

    renderTopicSuggestions(topics) {
        const container = document.getElementById('topicSuggestions');
        container.innerHTML = '';
        
        topics.forEach(topic => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'topic-btn';
            button.textContent = topic;
            button.addEventListener('click', () => {
                document.getElementById('topic').value = topic;
            });
            container.appendChild(button);
        });
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const ageGroup = formData.get('ageGroup');
        const topic = formData.get('topic');

        if (!ageGroup) {
            this.showError('Please select an age group');
            return;
        }

        this.setLoadingState(true);
        this.hideError();

        try {
            const devotional = await this.generateDevotional(ageGroup, topic);
            this.displayDevotional(devotional);
        } catch (error) {
            console.error('Error generating devotional:', error);
            this.showError('Failed to generate devotional. Please try again.');
        } finally {
            this.setLoadingState(false);
        }
    }

    async generateDevotional(ageGroup, topic) {
        const requestBody = {
            age_group: ageGroup,
            topic: topic || null
        };

        const response = await fetch(`${API_BASE_URL}/generate-devotional`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    displayDevotional(devotional) {
        // Update content with AOG format
        document.getElementById('devotionalTitle').textContent = devotional.title;
        document.getElementById('questionOfDay').textContent = devotional.question_of_day;
        document.getElementById('listenContent').textContent = devotional.listen_content;
        document.getElementById('learnContent').textContent = devotional.learn_content;
        document.getElementById('liveContent').textContent = devotional.live_content;
        document.getElementById('devotionalPrayer').textContent = devotional.prayer;

        // Update metadata
        const ageGroupTag = document.getElementById('ageGroupTag');
        ageGroupTag.textContent = this.formatAgeGroup(devotional.age_group);

        const topicTag = document.getElementById('topicTag');
        if (devotional.topic) {
            topicTag.textContent = `Topic: ${devotional.topic}`;
            topicTag.style.display = 'inline-block';
        } else {
            topicTag.style.display = 'none';
        }

        // Show result section
        document.getElementById('devotionalResult').style.display = 'block';
        
        // Scroll to result
        document.getElementById('devotionalResult').scrollIntoView({ 
            behavior: 'smooth' 
        });
    }

    formatAgeGroup(ageGroup) {
        const ageGroupMap = {
            'children': 'Children (5-12 years)',
            'teens': 'Teens (13-17 years)',
            'young_adults': 'Young Adults (18-25 years)',
            'adults': 'Adults (26+ years)'
        };
        return ageGroupMap[ageGroup] || ageGroup;
    }

    setLoadingState(isLoading) {
        const generateBtn = document.getElementById('generateBtn');
        const btnText = document.getElementById('btnText');
        const spinner = document.getElementById('loadingSpinner');

        generateBtn.disabled = isLoading;
        
        if (isLoading) {
            btnText.textContent = 'Generating...';
            spinner.style.display = 'block';
        } else {
            btnText.textContent = 'Generate Devotional';
            spinner.style.display = 'none';
        }
    }

    showError(message) {
        const errorElement = document.getElementById('errorMessage');
        errorElement.textContent = message;
        errorElement.style.display = 'block';
        errorElement.scrollIntoView({ behavior: 'smooth' });
    }

    hideError() {
        document.getElementById('errorMessage').style.display = 'none';
    }

    resetForm() {
        document.getElementById('devotionalForm').reset();
        document.getElementById('devotionalResult').style.display = 'none';
        this.hideError();
        
        // Scroll back to top
        document.querySelector('header').scrollIntoView({ behavior: 'smooth' });
    }

    printDevotional() {
        const devotionalCard = document.querySelector('.devotional-card');
        const printWindow = window.open('', '_blank');
        
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>AOG Family Devotional</title>
                <style>
                    body { 
                        font-family: Georgia, serif; 
                        line-height: 1.6; 
                        max-width: 600px; 
                        margin: 0 auto; 
                        padding: 20px;
                    }
                    h2 { 
                        color: #333; 
                        border-bottom: 2px solid #667eea; 
                        padding-bottom: 10px; 
                    }
                    h3 { 
                        color: #555; 
                        margin-top: 25px; 
                    }
                    blockquote { 
                        background: #f8f9fa; 
                        border-left: 4px solid #667eea; 
                        padding: 15px; 
                        font-style: italic; 
                        margin: 15px 0;
                    }
                    .content, .prayer { 
                        background: #f8f9fa; 
                        padding: 15px; 
                        border-radius: 5px; 
                        margin: 15px 0;
                    }
                    .metadata { 
                        text-align: center; 
                        color: #666; 
                        font-size: 0.9em; 
                        margin-top: 30px; 
                        border-top: 1px solid #ccc; 
                        padding-top: 15px;
                    }
                </style>
            </head>
            <body>
                ${devotionalCard.innerHTML}
                <div class="metadata">
                    <p>AOG Family Devotionals - Generated on ${new Date().toLocaleDateString()}</p>
                </div>
            </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.focus();
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 250);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DevotionalApp();
});