document.addEventListener('DOMContentLoaded', () => {
    // State management
    let state = {
        accounts: JSON.parse(localStorage.getItem('nexus_bank_data')) || {},
        currentView: 'dashboard',
        selectedAccountId: null
    };

    // DOM Elements
    const dashTab = document.getElementById('dash-tab');
    const accountsTab = document.getElementById('accounts-tab');
    const transactionsTab = document.getElementById('transactions-tab');
    const sections = document.querySelectorAll('.content-section');
    const accountListContainer = document.getElementById('account-list-container');
    const globalTxnList = document.getElementById('global-txn-list');
    const totalBalanceEl = document.getElementById('total-balance');
    const totalDepositsEl = document.getElementById('total-deposits');
    const totalWithdrawalsEl = document.getElementById('total-withdrawals');

    // Modals
    const addAccountBtn = document.getElementById('add-account-btn');
    const modalOverlay = document.getElementById('modal-overlay');
    const cancelModal = document.getElementById('cancel-modal');
    const saveAccountBtn = document.getElementById('save-account');
    const txnModalOverlay = document.getElementById('txn-modal-overlay');
    const cancelTxnModal = document.getElementById('cancel-txn-modal');
    const saveTxnBtn = document.getElementById('save-txn');

    // Detail Elements
    const detailSection = document.getElementById('account-details');
    const dashSection = document.getElementById('dashboard');
    const backBtn = document.getElementById('back-to-dash');
    const detailName = document.getElementById('detail-name');
    const detailNo = document.getElementById('detail-no');
    const txnTbody = document.getElementById('txn-tbody');
    const depositBtn = document.getElementById('deposit-btn');
    const withdrawBtn = document.getElementById('withdraw-btn');

    let pendingTxnType = null;

    // Helper functions
    const saveData = () => {
        localStorage.setItem('nexus_bank_data', JSON.stringify(state.accounts));
        render();
    };

    const calculateStats = () => {
        let balance = 0;
        let deposits = 0;
        let withdrawals = 0;

        Object.values(state.accounts).forEach(acc => {
            acc.transactions.forEach(txn => {
                const amt = parseFloat(txn.amount);
                if (txn.type === 'Deposit' || txn.type === 'Account Created') {
                    balance += amt;
                    if (txn.type === 'Deposit') deposits += amt;
                } else if (txn.type === 'Withdrawal') {
                    balance -= amt;
                    withdrawals += amt;
                }
            });
        });

        totalBalanceEl.textContent = `$${balance.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        totalDepositsEl.textContent = `$${deposits.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        totalWithdrawalsEl.textContent = `$${withdrawals.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    };

    const renderAccountList = () => {
        accountListContainer.innerHTML = '';
        const accounts = Object.entries(state.accounts);
        
        if (accounts.length === 0) {
            accountListContainer.innerHTML = '<p class="empty-msg">No accounts yet.</p>';
            return;
        }

        accounts.forEach(([id, acc]) => {
            const balance = acc.transactions.reduce((acc, curr) => {
                if (curr.type === 'Withdrawal') return acc - curr.amount;
                return acc + curr.amount;
            }, 0);

            const card = document.createElement('div');
            card.className = 'account-card';
            card.innerHTML = `
                <div class="acc-details">
                    <h4>${acc.name}</h4>
                    <p>#${id}</p>
                </div>
                <div class="acc-balance">
                    <strong>$${balance.toLocaleString(undefined, {minimumFractionDigits: 2})}</strong>
                </div>
            `;
            card.onclick = () => showAccountDetails(id);
            accountListContainer.appendChild(card);
        });
    };

    const renderGlobalTxns = () => {
        globalTxnList.innerHTML = '';
        let allTxns = [];
        Object.values(state.accounts).forEach(acc => {
            acc.transactions.forEach(t => allTxns.push({...t, holder: acc.name}));
        });

        allTxns.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        allTxns.slice(0, 5).forEach(txn => {
            const item = document.createElement('div');
            item.className = 'txn-item';
            item.innerHTML = `
                <div class="txn-info">
                    <p><strong>${txn.type}</strong> - ${txn.holder}</p>
                    <p style="font-size: 0.8rem; color: var(--text-dim)">${new Date(txn.date).toLocaleDateString()}</p>
                </div>
                <div class="txn-amt ${txn.type === 'Withdrawal' ? 'error' : 'success'}">
                    ${txn.type === 'Withdrawal' ? '-' : '+'}$${txn.amount.toLocaleString()}
                </div>
            `;
            globalTxnList.appendChild(item);
        });
    };

    const showAccountDetails = (id) => {
        state.selectedAccountId = id;
        const acc = state.accounts[id];
        detailName.textContent = acc.name;
        detailNo.textContent = `#${id}`;
        
        renderTxnHistory(acc.transactions);
        
        dashSection.classList.add('hidden');
        detailSection.classList.remove('hidden');
    };

    const renderTxnHistory = (transactions) => {
        txnTbody.innerHTML = '';
        [...transactions].reverse().forEach(txn => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(txn.date).toLocaleString()}</td>
                <td><span class="badge ${txn.type.toLowerCase().replace(' ', '-')}">${txn.type}</span></td>
                <td>${txn.description}</td>
                <td style="text-align: right; color: ${txn.type === 'Withdrawal' ? 'var(--error)' : 'var(--success)'}">
                    ${txn.type === 'Withdrawal' ? '-' : '+'}$${txn.amount.toFixed(2)}
                </td>
            `;
            txnTbody.appendChild(row);
        });
    };

    const render = () => {
        calculateStats();
        renderAccountList();
        renderGlobalTxns();
    };

    // Event Listeners
    addAccountBtn.onclick = () => modalOverlay.classList.remove('hidden');
    cancelModal.onclick = () => modalOverlay.classList.add('hidden');
    
    saveAccountBtn.onclick = () => {
        const name = document.getElementById('acc-name').value;
        const no = document.getElementById('acc-no').value;
        
        if (!name || !no) return alert('Please fill all fields');
        if (state.accounts[no]) return alert('Account number already exists');

        state.accounts[no] = {
            name: name,
            transactions: [{
                date: new Date().toISOString(),
                type: 'Account Created',
                amount: 0,
                description: 'Initial balance'
            }]
        };

        document.getElementById('acc-name').value = '';
        document.getElementById('acc-no').value = '';
        modalOverlay.classList.add('hidden');
        saveData();
    };

    backBtn.onclick = () => {
        detailSection.classList.add('hidden');
        dashSection.classList.remove('hidden');
    };

    depositBtn.onclick = () => {
        pendingTxnType = 'Deposit';
        document.getElementById('txn-modal-title').textContent = 'Deposit Funds';
        txnModalOverlay.classList.remove('hidden');
    };

    withdrawBtn.onclick = () => {
        pendingTxnType = 'Withdrawal';
        document.getElementById('txn-modal-title').textContent = 'Withdraw Funds';
        txnModalOverlay.classList.remove('hidden');
    };

    cancelTxnModal.onclick = () => txnModalOverlay.classList.add('hidden');

    saveTxnBtn.onclick = () => {
        const amt = parseFloat(document.getElementById('txn-amount').value);
        const desc = document.getElementById('txn-desc').value;

        if (isNaN(amt) || amt <= 0) return alert('Enter a valid amount');

        const acc = state.accounts[state.selectedAccountId];
        
        // Balance check for withdrawal
        if (pendingTxnType === 'Withdrawal') {
            const balance = acc.transactions.reduce((acc, curr) => {
                if (curr.type === 'Withdrawal') return acc - curr.amount;
                return acc + curr.amount;
            }, 0);
            if (amt > balance) return alert('Insufficient funds');
        }

        acc.transactions.push({
            date: new Date().toISOString(),
            type: pendingTxnType,
            amount: amt,
            description: desc || (pendingTxnType + ' transaction')
        });

        document.getElementById('txn-amount').value = '';
        document.getElementById('txn-desc').value = '';
        txnModalOverlay.classList.add('hidden');
        saveData();
        showAccountDetails(state.selectedAccountId);
    };

    // Navigation logic (simplified)
    const tabs = [dashTab, accountsTab, transactionsTab];
    tabs.forEach(tab => {
        tab.onclick = () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            // For now everything happens on dash or detail
            detailSection.classList.add('hidden');
            dashSection.classList.remove('hidden');
        };
    });

    // Initial render
    render();
});
