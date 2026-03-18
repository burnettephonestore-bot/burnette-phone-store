// Sample data store (in-memory/localStorage) for the prototype.
// In a real application, this would be backed by a server and database.

const DEFAULT_DATA = {
  siteSettings: {
    title: 'Burnette Phone Store',
    logoUrl: 'https://via.placeholder.com/120x60?text=Burnette+Phone',
    themeColor: '#0d6efd',
    adminUsername: 'hudhaifa',
    adminPassword: '123',
    adminName: 'Hudhaifa',
    adminEmail: 'hudhaifabashiru@gmail.com',
    adminPhone: '0626905105'
  },
  products: [
    {
      id: 'p1',
      name: 'Burnette Plus 10',
      price: 299000,
      description: 'A powerful smartphone with long battery and crisp display.',
      mediaType: 'image',
      mediaUrl: 'https://images.unsplash.com/photo-1512499617640-c2f999018b72?auto=format&fit=crop&w=800&q=80'
    },
    {
      id: 'p2',
      name: 'Burnette Lite',
      price: 149000,
      description: 'Affordable and reliable phone for everyday use.',
      mediaType: 'image',
      mediaUrl: 'https://images.unsplash.com/photo-1512499617640-c2f999018b72?auto=format&fit=crop&w=800&q=80'
    },
    {
      id: 'p3',
      name: 'Burnette Pro Camera',
      price: 399000,
      description: 'Great for photography with enhanced camera features.',
      mediaType: 'video',
      mediaUrl: 'https://samplelib.com/lib/preview/mp4/sample-5s.mp4'
    }
  ],
  updates: [
    {
      id: 'u1',
      title: 'Flash Sale: 10% off on all phones',
      type: 'text',
      content: 'For the next 24 hours, enjoy a 10% discount on every phone in stock! Limited quantities available.',
      validUntil: null
    },
    {
      id: 'u2',
      title: 'New arrival: Burnette Ultra',
      type: 'image',
      content: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80',
      validUntil: null
    }
  ],
  requests: [],
  payments: {
    banks: [
      { id: 'b1', name: 'NMB Bank', accountNumber: '1234567890' },
      { id: 'b2', name: 'CRDB Bank', accountNumber: '0987654321' }
    ],
    mobileMoney: [
      { id: 'm1', name: 'M-Pesa', number: '0700123456' },
      { id: 'm2', name: 'Tigo Pesa', number: '0761234567' }
    ]
  ],
  comments: []
};

function loadData() {
  const raw = localStorage.getItem('burnetteData');
  if (!raw) {
    localStorage.setItem('burnetteData', JSON.stringify(DEFAULT_DATA));
    return JSON.parse(JSON.stringify(DEFAULT_DATA));
  }
  try {
    return JSON.parse(raw);
  } catch (err) {
    console.warn('Failed to parse stored data; resetting to defaults.', err);
    localStorage.setItem('burnetteData', JSON.stringify(DEFAULT_DATA));
    return JSON.parse(JSON.stringify(DEFAULT_DATA));
  }
}

function saveData(data) {
  localStorage.setItem('burnetteData', JSON.stringify(data));
}

const store = {
  data: loadData(),
  save() {
    saveData(this.data);
  }
};
