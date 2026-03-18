/* Burnette Phone Store frontend logic */

function formatCurrency(num) {
  return new Intl.NumberFormat('en-TZ', {
    style: 'currency',
    currency: 'TZS',
    maximumFractionDigits: 0
  }).format(num);
}

function getQueryParam(name) {
  const url = new URL(window.location.href);
  return url.searchParams.get(name);
}

function tapLogoEasterEgg(element, callback) {
  element.addEventListener('dblclick', (e) => {
    e.preventDefault();
    callback();
  });
}

function initSiteShell() {
  const data = store.data;
  const titleEl = document.querySelector('[data-site-title]');
  const logoEl = document.querySelector('[data-site-logo]');
  const headerTitleEl = document.querySelector('[data-site-header]');
  const brandEl = document.querySelector('.navbar-brand');

  if (titleEl) titleEl.textContent = data.siteSettings.title;
  if (headerTitleEl) headerTitleEl.textContent = data.siteSettings.title;
  if (logoEl) {
    if (data.siteSettings.logoUrl) {
      logoEl.src = data.siteSettings.logoUrl;
    }
  }
  if (brandEl) {
    // Long press for admin access
    let pressTimer;
    const startPress = () => {
      pressTimer = setTimeout(() => {
        window.location.href = 'admin-login.html';
      }, 2000); // 2 seconds
    };
    const cancelPress = () => {
      clearTimeout(pressTimer);
    };
    brandEl.addEventListener('mousedown', startPress);
    brandEl.addEventListener('touchstart', startPress);
    brandEl.addEventListener('mouseup', cancelPress);
    brandEl.addEventListener('touchend', cancelPress);
    brandEl.addEventListener('mouseleave', cancelPress); // for mouse
  }

  // Keyboard shortcut for admin (backup)
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'a') {
      e.preventDefault();
      window.location.href = 'admin-login.html';
    }
  });

  // Apply theme color
  if (data.siteSettings.themeColor) {
    document.documentElement.style.setProperty('--theme-color', data.siteSettings.themeColor);
  }
}

function initOffcanvas() {
  const offcanvasToggle = document.querySelector('[data-bs-toggle="offcanvas"]');
  if (!offcanvasToggle) return;
  offcanvasToggle.addEventListener('click', () => {
    const offcanvas = document.querySelector(offcanvasToggle.getAttribute('data-bs-target'));
    if (offcanvas) {
      const bs = bootstrap.Offcanvas.getOrCreateInstance(offcanvas);
      bs.toggle();
    }
  });
}

function initNavbarActive() {
  const current = window.location.pathname.split('/').pop();
  document.querySelectorAll('[data-nav-page]').forEach((el) => {
    const target = el.getAttribute('data-nav-page');
    if (target === current || (current === '' && target === 'index.html')) {
      el.classList.add('active');
    } else {
      el.classList.remove('active');
    }
  });
}

function initCommon() {
  initSiteShell();
  initOffcanvas();
  initNavbarActive();
}

// Products page
function renderProductsPage() {
  const productGrid = document.getElementById('productGrid');
  if (!productGrid) return;
  productGrid.innerHTML = '';
  store.data.products.forEach((product) => {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-4';
    col.innerHTML = `
      <div class="card h-100 shadow-sm">
        ${product.mediaType === 'video' ?
          `<video class="card-img-top" controls muted><source src="${product.mediaUrl}" type="video/mp4">Your browser does not support video.</video>` :
          `<img src="${product.mediaUrl}" class="card-img-top" alt="${product.name}">`}
        <div class="card-body d-flex flex-column">
          <h5 class="card-title">${product.name}</h5>
          <p class="card-text flex-grow-1">${product.description}</p>
          <p class="card-text fw-bold mb-2">${formatCurrency(product.price)}</p>
          <a href="request.html?productId=${product.id}" class="btn btn-primary">Request</a>
        </div>
      </div>
    `;
    productGrid.appendChild(col);
  });
}

// Updates page
function renderUpdatesPage() {
  const updatesGrid = document.getElementById('updatesGrid');
  if (!updatesGrid) return;
  updatesGrid.innerHTML = '';
  const now = new Date();

  store.data.updates.forEach((update) => {
    // skip expired
    if (update.validUntil && new Date(update.validUntil) < now) {
      return;
    }

    const col = document.createElement('div');
    col.className = 'col-md-6 mb-4';
    let body = '';
    if (update.type === 'image') {
      body = `<img src="${update.content}" class="img-fluid rounded mb-3" alt="${update.title}">`;
    } else if (update.type === 'video') {
      body = `<video class="w-100 mb-3" controls muted><source src="${update.content}" type="video/mp4">Your browser does not support video.</video>`;
    } else {
      body = `<p>${update.content}</p>`;
    }

    col.innerHTML = `
      <div class="card shadow-sm h-100">
        <div class="card-body">
          <h5 class="card-title">${update.title}</h5>
          ${body}
          ${update.validUntil ? `<p class="text-muted small">Valid until ${new Date(update.validUntil).toLocaleString()}</p>` : ''}
        </div>
      </div>
    `;
    updatesGrid.appendChild(col);
  });
}

// Request page
function initRequestPage() {
  const productId = getQueryParam('productId');
  const product = store.data.products.find((p) => p.id === productId);
  const productNameEl = document.getElementById('requestProductName');
  const productPriceEl = document.getElementById('requestProductPrice');
  const productIdInput = document.getElementById('requestProductId');
  const finalPriceEl = document.getElementById('finalPrice');
  const discountInput = document.getElementById('discount');
  const paymentMethodRadios = document.querySelectorAll('input[name="paymentMethod"]');
  const paymentDetails = document.getElementById('paymentDetails');
  const regionSelect = document.getElementById('region');
  const districtSelect = document.getElementById('district');
  const deliveryFields = document.getElementById('deliveryFields');

  if (product) {
    if (productNameEl) productNameEl.textContent = product.name;
    if (productPriceEl) productPriceEl.textContent = formatCurrency(product.price);
    if (productIdInput) productIdInput.value = product.id;
    if (finalPriceEl) finalPriceEl.textContent = formatCurrency(product.price);
  }

  function updateFinalPrice() {
    const discount = Number(discountInput?.value || 0);
    const base = product ? product.price : 0;
    const final = Math.max(0, base - discount);
    if (finalPriceEl) finalPriceEl.textContent = formatCurrency(final);
  }

  if (discountInput) {
    discountInput.addEventListener('input', updateFinalPrice);
  }

  function renderPaymentDetails(method) {
    if (!paymentDetails) return;
    const payments = store.data.payments;
    if (method === 'bank') {
      paymentDetails.innerHTML = `
        <div class="mb-3">
          <label class="form-label">Select bank account</label>
          <select class="form-select" id="bankAccount" required>
            <option value="">Choose an account</option>
            ${payments.banks.map((b) => `<option value="${b.id}">${b.name} — ${b.accountNumber}</option>`).join('')}
          </select>
        </div>
      `;
    } else {
      paymentDetails.innerHTML = `
        <div class="mb-3">
          <label class="form-label">Select mobile money</label>
          <select class="form-select" id="mobileMoney" required>
            <option value="">Choose a service</option>
            ${payments.mobileMoney.map((m) => `<option value="${m.id}">${m.name} — ${m.number}</option>`).join('')}
          </select>
        </div>
      `;
    }
  }

  if (paymentMethodRadios.length) {
    paymentMethodRadios.forEach((radio) => {
      radio.addEventListener('change', () => {
        renderPaymentDetails(radio.value);
      });
      if (radio.checked) {
        renderPaymentDetails(radio.value);
      }
    });
  }

  function renderRegionOptions() {
    if (!regionSelect) return;
    regionSelect.innerHTML = `<option value="">Select a region</option>` +
      TZ_REGIONS.map((r) => `<option value="${r.name}">${r.name}</option>`).join('');
  }

  function renderDistrictOptions(regionName) {
    if (!districtSelect) return;
    const region = TZ_REGIONS.find((r) => r.name === regionName);
    if (!region) {
      districtSelect.innerHTML = `<option value="">Select a district</option>`;
      return;
    }
    districtSelect.innerHTML = `<option value="">Select a district</option>` +
      region.districts.map((d) => `<option value="${d}">${d}</option>`).join('');
  }

  if (regionSelect) {
    renderRegionOptions();
    regionSelect.addEventListener('change', (event) => {
      renderDistrictOptions(event.target.value);
    });
  }

  const deliveryYes = document.getElementById('deliveryYes');
  const deliveryNo = document.getElementById('deliveryNo');
  if (deliveryYes && deliveryNo && deliveryFields) {
    function toggleDelivery(show) {
      deliveryFields.style.display = show ? 'block' : 'none';
      const inputs = deliveryFields.querySelectorAll('input, select');
      inputs.forEach((i) => {
        i.required = show;
      });
    }
    deliveryYes.addEventListener('change', () => toggleDelivery(true));
    deliveryNo.addEventListener('change', () => toggleDelivery(false));
    // default
    toggleDelivery(false);
  }

  const requestForm = document.getElementById('requestForm');
  if (requestForm) {
    requestForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(requestForm);
      const request = {
        id: `r_${Date.now()}`,
        productId: formData.get('productId'),
        productName: product?.name || '',
        basePrice: product?.price || 0,
        discount: Number(formData.get('discount') || 0),
        explanation: formData.get('explanation'),
        contactName: formData.get('contactName'),
        contactPhone: formData.get('contactPhone'),
        contactEmail: formData.get('contactEmail'),
        wantsDelivery: formData.get('delivery') === 'yes',
        region: formData.get('region'),
        district: formData.get('district'),
        address: formData.get('address'),
        paymentMethod: formData.get('paymentMethod'),
        paymentTarget: formData.get('bankAccount') || formData.get('mobileMoney') || '',
        status: 'pending',
        createdAt: new Date().toISOString()
      };
      store.data.requests.unshift(request);
      store.save();
      alert('Request submitted! An admin will review and respond shortly.');
      requestForm.reset();
      updateFinalPrice();
    });
  }
}

// Admin login
function initAdminLogin() {
  const loginForm = document.getElementById('adminLoginForm');
  const errorAlert = document.getElementById('adminLoginError');

  if (!loginForm) return;

  loginForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = new FormData(loginForm);
    const username = data.get('username').toLowerCase();
    const password = data.get('password');

    console.log('Login attempt:', username, password);

    const settings = store.data.siteSettings;
    if (username === settings.adminUsername.toLowerCase() && password === settings.adminPassword) {
      console.log('Login successful');
      localStorage.setItem('burnetteAdminAuth', 'true');
      window.location.href = 'admin-dashboard.html';
      return;
    }

    console.log('Login failed');
    if (errorAlert) {
      errorAlert.textContent = 'Invalid credentials. Please try again.';
      errorAlert.style.display = 'block';
    }
  });
}

function requireAdminAuth() {
  const auth = localStorage.getItem('burnetteAdminAuth');
  if (auth !== 'true') {
    window.location.href = 'admin-login.html';
    return false;
  }
  return true;
}

function initAdminDashboard() {
  if (!requireAdminAuth()) return;

  const cardProducts = document.getElementById('cardProducts');
  const cardUpdates = document.getElementById('cardUpdates');
  const cardRequests = document.getElementById('cardRequests');
  const cardComments = document.getElementById('cardComments');

  const now = new Date();
  const requestTrend = store.data.requests.slice(0, 30).map((r) => ({
    date: new Date(r.createdAt).toLocaleDateString(),
    status: r.status
  }));

  if (cardProducts) cardProducts.textContent = store.data.products.length;
  if (cardUpdates) cardUpdates.textContent = store.data.updates.length;
  if (cardRequests) cardRequests.textContent = store.data.requests.length;
  if (cardComments) cardComments.textContent = store.data.comments.length;

  // Charts
  const requestsChart = document.getElementById('requestsChart');
  if (requestsChart) {
    const counts = {};
    requestTrend.forEach((r) => {
      counts[r.date] = (counts[r.date] || 0) + 1;
    });
    const labels = Object.keys(counts).slice(-10);
    const values = labels.map((l) => counts[l]);

    new Chart(requestsChart.getContext('2d'), {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Requests',
          data: values,
          borderColor: getComputedStyle(document.documentElement).getPropertyValue('--theme-color') || '#0d6efd',
          backgroundColor: 'rgba(13, 110, 253, 0.2)',
          fill: true
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  // Setup logout
  const logoutBtn = document.getElementById('adminLogout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      localStorage.removeItem('burnetteAdminAuth');
      window.location.href = 'index.html';
    });
  }

  // Setup side nav links
  document.querySelectorAll('[data-admin-tab]').forEach((tab) => {
    tab.addEventListener('click', (event) => {
      event.preventDefault();
      document.querySelectorAll('.admin-tab-content').forEach((el) => el.classList.add('d-none'));
      document.querySelectorAll('[data-admin-tab]').forEach((el) => el.classList.remove('active'));
      const target = tab.getAttribute('data-admin-tab');
      const section = document.getElementById(target);
      if (section) section.classList.remove('d-none');
      tab.classList.add('active');
      if (target === 'tab-products') renderAdminProducts();
      if (target === 'tab-updates') renderAdminUpdates();
      if (target === 'tab-requests') renderAdminRequests();
      if (target === 'tab-payments') renderAdminPayments();
      if (target === 'tab-comments') renderAdminComments();
      if (target === 'tab-settings') renderAdminSettings();
    });
  });

  // Activate first tab
  const firstTab = document.querySelector('[data-admin-tab]');
  if (firstTab) firstTab.click();
}

function renderAdminProducts() {
  const list = document.getElementById('adminProductsList');
  if (!list) return;
  list.innerHTML = '';
  store.data.products.forEach((product) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${product.name}</td>
      <td>${formatCurrency(product.price)}</td>
      <td>${product.mediaType}</td>
      <td>
        <button class="btn btn-sm btn-outline-primary me-1" data-action="edit" data-id="${product.id}">Edit</button>
        <button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${product.id}">Delete</button>
      </td>
    `;
    list.appendChild(row);
  });

  const createBtn = document.getElementById('adminProductsCreate');
  if (createBtn) {
    createBtn.onclick = () => openProductModal();
  }

  list.querySelectorAll('button[data-action]').forEach((btn) => {
    const action = btn.getAttribute('data-action');
    const id = btn.getAttribute('data-id');
    btn.addEventListener('click', () => {
      if (action === 'edit') openProductModal(id);
      if (action === 'delete') {
        if (confirm('Delete this product?')) {
          store.data.products = store.data.products.filter((p) => p.id !== id);
          store.save();
          renderAdminProducts();
        }
      }
    });
  });
}

function openProductModal(productId) {
  const modalEl = document.getElementById('productModal');
  const modal = new bootstrap.Modal(modalEl);
  const form = modalEl.querySelector('form');
  const titleEl = modalEl.querySelector('.modal-title');
  const product = store.data.products.find((p) => p.id === productId);

  const fields = {
    id: form.querySelector('[name="id"]'),
    name: form.querySelector('[name="name"]'),
    price: form.querySelector('[name="price"]'),
    description: form.querySelector('[name="description"]'),
    mediaUrl: form.querySelector('[name="mediaUrl"]'),
    mediaType: form.querySelector('[name="mediaType"]')
  };

  if (product) {
    titleEl.textContent = 'Edit Product';
    fields.id.value = product.id;
    fields.name.value = product.name;
    fields.price.value = product.price;
    fields.description.value = product.description;
    fields.mediaUrl.value = product.mediaUrl;
    fields.mediaType.value = product.mediaType;
  } else {
    titleEl.textContent = 'Create Product';
    fields.id.value = '';
    fields.name.value = '';
    fields.price.value = '';
    fields.description.value = '';
    fields.mediaUrl.value = '';
    fields.mediaType.value = 'image';
  }

  form.onsubmit = (event) => {
    event.preventDefault();
    const newProduct = {
      id: fields.id.value || `p_${Date.now()}`,
      name: fields.name.value,
      price: Number(fields.price.value || 0),
      description: fields.description.value,
      mediaUrl: fields.mediaUrl.value,
      mediaType: fields.mediaType.value
    };
    if (product) {
      const index = store.data.products.findIndex((p) => p.id === newProduct.id);
      store.data.products[index] = newProduct;
    } else {
      store.data.products.unshift(newProduct);
    }
    store.save();
    modal.hide();
    renderAdminProducts();
  };

  modal.show();
}

function renderAdminUpdates() {
  const list = document.getElementById('adminUpdatesList');
  if (!list) return;
  list.innerHTML = '';
  store.data.updates.forEach((update) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${update.title}</td>
      <td>${update.type}</td>
      <td>${update.validUntil ? new Date(update.validUntil).toLocaleString() : 'N/A'}</td>
      <td>
        <button class="btn btn-sm btn-outline-primary me-1" data-action="edit" data-id="${update.id}">Edit</button>
        <button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${update.id}">Delete</button>
      </td>
    `;
    list.appendChild(row);
  });

  const createBtn = document.getElementById('adminUpdatesCreate');
  if (createBtn) {
    createBtn.onclick = () => openUpdateModal();
  }

  list.querySelectorAll('button[data-action]').forEach((btn) => {
    const action = btn.getAttribute('data-action');
    const id = btn.getAttribute('data-id');
    btn.addEventListener('click', () => {
      if (action === 'edit') openUpdateModal(id);
      if (action === 'delete') {
        if (confirm('Delete this update?')) {
          store.data.updates = store.data.updates.filter((u) => u.id !== id);
          store.save();
          renderAdminUpdates();
        }
      }
    });
  });
}

function openUpdateModal(updateId) {
  const modalEl = document.getElementById('updateModal');
  const modal = new bootstrap.Modal(modalEl);
  const form = modalEl.querySelector('form');
  const titleEl = modalEl.querySelector('.modal-title');

  const update = store.data.updates.find((u) => u.id === updateId);

  const fields = {
    id: form.querySelector('[name="id"]'),
    title: form.querySelector('[name="title"]'),
    type: form.querySelector('[name="type"]'),
    content: form.querySelector('[name="content"]'),
    validUntil: form.querySelector('[name="validUntil"]')
  };

  if (update) {
    titleEl.textContent = 'Edit Update';
    fields.id.value = update.id;
    fields.title.value = update.title;
    fields.type.value = update.type;
    fields.content.value = update.content;
    fields.validUntil.value = update.validUntil ? update.validUntil.split('T')[0] : '';
  } else {
    titleEl.textContent = 'Create Update';
    fields.id.value = '';
    fields.title.value = '';
    fields.type.value = 'text';
    fields.content.value = '';
    fields.validUntil.value = '';
  }

  function updateContentLabel() {
    const label = modalEl.querySelector('[data-content-label]');
    if (label) {
      label.textContent = fields.type.value === 'text' ? 'Text message' : (fields.type.value === 'image' ? 'Image URL' : 'Video URL');
    }
  }

  fields.type.addEventListener('change', updateContentLabel);
  updateContentLabel();

  form.onsubmit = (event) => {
    event.preventDefault();
    const newUpdate = {
      id: fields.id.value || `u_${Date.now()}`,
      title: fields.title.value,
      type: fields.type.value,
      content: fields.content.value,
      validUntil: fields.validUntil.value ? new Date(fields.validUntil.value).toISOString() : null
    };
    if (update) {
      const idx = store.data.updates.findIndex((u) => u.id === newUpdate.id);
      store.data.updates[idx] = newUpdate;
    } else {
      store.data.updates.unshift(newUpdate);
    }
    store.save();
    modal.hide();
    renderAdminUpdates();
  };

  modal.show();
}

function renderAdminRequests() {
  const table = document.getElementById('adminRequestsTable');
  if (!table) return;
  const body = table.querySelector('tbody');
  body.innerHTML = '';
  store.data.requests.forEach((req) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${new Date(req.createdAt).toLocaleString()}</td>
      <td>${req.productName}</td>
      <td>${formatCurrency(req.basePrice)}</td>
      <td>${formatCurrency(req.discount)}</td>
      <td>${req.contactPhone || req.contactEmail}</td>
      <td>${req.wantsDelivery ? 'Yes' : 'No'}</td>
      <td>${req.paymentMethod}</td>
      <td>
        <select class="form-select form-select-sm" data-action="status" data-id="${req.id}">
          <option value="pending" ${req.status === 'pending' ? 'selected' : ''}>Pending</option>
          <option value="approved" ${req.status === 'approved' ? 'selected' : ''}>Approved</option>
          <option value="rejected" ${req.status === 'rejected' ? 'selected' : ''}>Rejected</option>
        </select>
      </td>
      <td>
        <button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${req.id}">Delete</button>
      </td>
    `;
    body.appendChild(row);
  });

  table.querySelectorAll('select[data-action="status"]').forEach((select) => {
    select.addEventListener('change', () => {
      const id = select.getAttribute('data-id');
      const req = store.data.requests.find((r) => r.id === id);
      if (req) {
        req.status = select.value;
        store.save();
      }
    });
  });

  table.querySelectorAll('button[data-action="delete"]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
      if (confirm('Delete request?')) {
        store.data.requests = store.data.requests.filter((r) => r.id !== id);
        store.save();
        renderAdminRequests();
      }
    });
  });
}

function renderAdminPayments() {
  const bankList = document.getElementById('paymentBanksList');
  const mobileList = document.getElementById('paymentMobileList');

  if (!bankList || !mobileList) return;

  function renderTable(listEl, items, type) {
    listEl.innerHTML = '';
    items.forEach((item) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${item.name}</td>
        <td>${item.accountNumber || item.number}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" data-type="${type}" data-action="edit" data-id="${item.id}">Edit</button>
          <button class="btn btn-sm btn-outline-danger" data-type="${type}" data-action="delete" data-id="${item.id}">Delete</button>
        </td>
      `;
      listEl.appendChild(row);
    });
  }

  renderTable(bankList, store.data.payments.banks, 'bank');
  renderTable(mobileList, store.data.payments.mobileMoney, 'mobile');

  document.querySelectorAll('#paymentBanksList button, #paymentMobileList button').forEach((btn) => {
    const action = btn.getAttribute('data-action');
    const id = btn.getAttribute('data-id');
    const type = btn.getAttribute('data-type');
    btn.addEventListener('click', () => {
      if (action === 'edit') openPaymentModal(type, id);
      if (action === 'delete') {
        if (confirm('Delete this payment entry?')) {
          if (type === 'bank') {
            store.data.payments.banks = store.data.payments.banks.filter((b) => b.id !== id);
          } else {
            store.data.payments.mobileMoney = store.data.payments.mobileMoney.filter((m) => m.id !== id);
          }
          store.save();
          renderAdminPayments();
        }
      }
    });
  });

  document.getElementById('paymentAddBank')?.addEventListener('click', () => openPaymentModal('bank'));
  document.getElementById('paymentAddMobile')?.addEventListener('click', () => openPaymentModal('mobile'));
}

function openPaymentModal(type, id) {
  const modalEl = document.getElementById('paymentModal');
  const modal = new bootstrap.Modal(modalEl);
  const form = modalEl.querySelector('form');
  const titleEl = modalEl.querySelector('.modal-title');

  const title = type === 'bank' ? 'Bank Account' : 'Mobile Money';
  titleEl.textContent = id ? `Edit ${title}` : `Add ${title}`;

  const record = (type === 'bank' ? store.data.payments.banks : store.data.payments.mobileMoney).find((x) => x.id === id);

  const fields = {
    id: form.querySelector('[name="id"]'),
    type: form.querySelector('[name="type"]'),
    name: form.querySelector('[name="name"]'),
    number: form.querySelector('[name="number"]')
  };

  fields.type.value = type;
  if (record) {
    fields.id.value = record.id;
    fields.name.value = record.name;
    fields.number.value = record.accountNumber || record.number;
  } else {
    fields.id.value = '';
    fields.name.value = '';
    fields.number.value = '';
  }

  form.onsubmit = (event) => {
    event.preventDefault();
    const entry = {
      id: fields.id.value || `${type}_${Date.now()}`,
      name: fields.name.value,
      accountNumber: type === 'bank' ? fields.number.value : undefined,
      number: type === 'mobile' ? fields.number.value : undefined
    };
    if (record) {
      if (type === 'bank') {
        store.data.payments.banks = store.data.payments.banks.map((b) => (b.id === entry.id ? entry : b));
      } else {
        store.data.payments.mobileMoney = store.data.payments.mobileMoney.map((m) => (m.id === entry.id ? entry : m));
      }
    } else {
      if (type === 'bank') store.data.payments.banks.push(entry);
      else store.data.payments.mobileMoney.push(entry);
    }
    store.save();
    modal.hide();
    renderAdminPayments();
  };

  modal.show();
}

function renderAdminComments() {
  const list = document.getElementById('adminCommentsList');
  if (!list) return;
  list.innerHTML = '';
  store.data.comments.forEach((comment) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${comment.name}</td>
      <td>${comment.message}</td>
      <td>${new Date(comment.createdAt).toLocaleString()}</td>
      <td>
        <select class="form-select form-select-sm" data-action="status" data-id="${comment.id}">
          <option value="pending" ${comment.status === 'pending' ? 'selected' : ''}>Pending</option>
          <option value="approved" ${comment.status === 'approved' ? 'selected' : ''}>Approved</option>
          <option value="rejected" ${comment.status === 'rejected' ? 'selected' : ''}>Rejected</option>
        </select>
      </td>
      <td>
        <button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${comment.id}">Delete</button>
      </td>
    `;
    list.appendChild(row);
  });

  list.querySelectorAll('select[data-action="status"]').forEach((select) => {
    select.addEventListener('change', () => {
      const id = select.getAttribute('data-id');
      const comment = store.data.comments.find((c) => c.id === id);
      if (comment) {
        comment.status = select.value;
        store.save();
      }
    });
  });

  list.querySelectorAll('button[data-action="delete"]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-id');
      if (confirm('Delete comment?')) {
        store.data.comments = store.data.comments.filter((c) => c.id !== id);
        store.save();
        renderAdminComments();
      }
    });
  });
}

function renderAdminSettings() {
  const form = document.getElementById('settingsForm');
  if (!form) return;
  const settings = store.data.siteSettings;
  form.siteTitle.value = settings.title;
  form.logoUrl.value = settings.logoUrl;
  form.themeColor.value = settings.themeColor;
  form.adminUsername.value = settings.adminUsername;
  form.adminPassword.value = settings.adminPassword;
  form.adminName.value = settings.adminName;
  form.adminEmail.value = settings.adminEmail;
  form.adminPhone.value = settings.adminPhone;

  form.onsubmit = (event) => {
    event.preventDefault();
    settings.title = form.siteTitle.value;
    settings.logoUrl = form.logoUrl.value;
    settings.themeColor = form.themeColor.value;
    settings.adminUsername = form.adminUsername.value;
    settings.adminPassword = form.adminPassword.value;
    settings.adminName = form.adminName.value;
    settings.adminEmail = form.adminEmail.value;
    settings.adminPhone = form.adminPhone.value;
    store.save();
    initSiteShell();
    alert('Settings saved.');
  };
}

// Check for admin access via URL
if (window.location.search.includes('admin')) {
  window.location.href = 'admin-login.html';
}

// Initialize common UI behavior once the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  initCommon();
});
