// Real-time expenses functionality
document.addEventListener('DOMContentLoaded', function() {
    // Function to update dashboard data without page refresh
    function updateDashboardData() {
        fetch('/api/dashboard-data/')
            .then(response => response.json())
            .then(data => {
                // Update income, expenses, and net profit on dashboard
                const incomeElement = document.querySelector('[data-income]');
                const expensesElement = document.querySelector('[data-expenses]');
                const netProfitElement = document.querySelector('[data-net-profit]');
                
                if (incomeElement) {
                    incomeElement.textContent = '$' + data.monthly_income[data.monthly_income.length - 1].toFixed(2);
                }
                
                if (expensesElement) {
                    expensesElement.textContent = '$' + data.monthly_expenses[data.monthly_expenses.length - 1].toFixed(2);
                }
                
                if (netProfitElement) {
                    const netProfit = data.monthly_income[data.monthly_income.length - 1] - 
                                     data.monthly_expenses[data.monthly_expenses.length - 1];
                    netProfitElement.textContent = '$' + netProfit.toFixed(2);
                }
                
                // Update charts if they exist
                if (window.cashFlowChart) {
                    window.cashFlowChart.data.datasets[0].data = data.monthly_income;
                    window.cashFlowChart.data.datasets[1].data = data.monthly_expenses;
                    window.cashFlowChart.data.labels = data.months;
                    window.cashFlowChart.update();
                }
                
                // Update expense breakdown chart
                if (window.expenseChart) {
                    window.expenseChart.data.labels = data.expense_categories.labels;
                    window.expenseChart.data.datasets[0].data = data.expense_categories.values;
                    window.expenseChart.update();
                }
            })
            .catch(error => {
                console.error('Error fetching dashboard data:', error);
            });
    }

    // Auto-refresh dashboard data every 30 seconds
    if (document.querySelector('#cashFlowChart') || document.querySelector('#expenseChart')) {
        setInterval(updateDashboardData, 30000);
    }

    // Handle form submissions with AJAX for real-time updates
    const transactionForm = document.querySelector('#transaction-form');
    if (transactionForm) {
        transactionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(transactionForm);
            const submitButton = transactionForm.querySelector('button[type="submit"]');
            
            // Disable submit button to prevent duplicate submissions
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
            
            fetch('/transactions/create/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showMessage('Transaction created successfully!', 'success');
                    
                    // Reset form
                    transactionForm.reset();
                    
                    // Update dashboard data
                    updateDashboardData();
                    
                    // Update transaction list if on transactions page
                    if (document.querySelector('#transactions-table')) {
                        loadRecentTransactions();
                    }
                } else {
                    showMessage(data.message || 'Error creating transaction', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('An error occurred while creating transaction', 'error');
            })
            .finally(() => {
                // Re-enable submit button
                submitButton.disabled = false;
                submitButton.innerHTML = 'Create Transaction';
            });
        });
    }

    // Function to load recent transactions
    function loadRecentTransactions() {
        fetch('/api/recent-transactions/')
            .then(response => response.json())
            .then(data => {
                const transactionsContainer = document.querySelector('#recent-transactions');
                if (transactionsContainer) {
                    let html = '';
                    data.transactions.forEach(transaction => {
                        html += `
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${transaction.date}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${transaction.description}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    <span class="${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}">
                                        ${transaction.type === 'income' ? '+' : '-'}$${transaction.amount}
                                    </span>
                                </td>
                            </tr>
                        `;
                    });
                    transactionsContainer.innerHTML = html;
                }
            })
            .catch(error => {
                console.error('Error loading transactions:', error);
            });
    }

    // Function to show messages
    function showMessage(message, type) {
        // Remove existing messages
        const existingMessages = document.querySelectorAll('.alert-message');
        existingMessages.forEach(msg => msg.remove());
        
        // Create message element
        const messageElement = document.createElement('div');
        messageElement.className = `alert-message fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'
        }`;
        messageElement.textContent = message;
        
        document.body.appendChild(messageElement);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            messageElement.remove();
        }, 5000);
    }

    // Function to handle transaction deletion with AJAX
    document.querySelectorAll('.delete-transaction').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const transactionId = this.dataset.transactionId;
            if (confirm('Are you sure you want to delete this transaction?')) {
                fetch(`/transactions/${transactionId}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showMessage('Transaction deleted successfully!', 'success');
                        
                        // Update dashboard data
                        updateDashboardData();
                        
                        // Remove transaction from list
                        this.closest('tr').remove();
                    } else {
                        showMessage(data.message || 'Error deleting transaction', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('An error occurred while deleting transaction', 'error');
                });
            }
        });
    });

    // Real-time search for transactions
    const searchInput = document.querySelector('#transaction-search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value;
                if (query.length > 2 || query.length === 0) {
                    loadFilteredTransactions(query);
                }
            }, 500);
        });
    }

    // Function to load filtered transactions
    function loadFilteredTransactions(query) {
        let url = '/transactions/';
        if (query) {
            url += `?search=${encodeURIComponent(query)}`;
        }
        
        fetch(url)
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newTableBody = doc.querySelector('tbody');
                
                if (newTableBody) {
                    const currentTableBody = document.querySelector('tbody');
                    if (currentTableBody) {
                        currentTableBody.innerHTML = newTableBody.innerHTML;
                    }
                }
            })
            .catch(error => {
                console.error('Error loading filtered transactions:', error);
            });
    }
});