// Compiled-from-handwritten-TS: lightweight JS client exposing window.BlindDateApi
(function(){
  function ApiClient(baseUrl){
    this.baseUrl = baseUrl || '';
    this.token = null;
  }
  ApiClient.prototype.setToken = function(t){ this.token = t };
  ApiClient.prototype._headers = function(){
    var h = { 'Content-Type': 'application/json' };
    if(this.token) h['Authorization'] = 'Bearer ' + this.token;
    return h;
  };
  ApiClient.prototype.parseAgent = function(text, session_id){
    var self = this;
    return fetch(this.baseUrl + '/api/agent/parse', { method: 'POST', headers: this._headers(), body: JSON.stringify({ text: text, session_id: session_id }) })
      .then(function(res){ if(!res.ok) throw new Error('parseAgent failed: ' + res.status); return res.json(); });
  };
  ApiClient.prototype.aiDecide = function(payload){
    return fetch(this.baseUrl + '/api/ai/decide', { method: 'POST', headers: this._headers(), body: JSON.stringify(payload) })
      .then(function(res){ if(!res.ok) throw new Error('aiDecide failed: ' + res.status); return res.json(); });
  };
  ApiClient.prototype.checkout = function(payload){
    return fetch(this.baseUrl + '/api/checkout', { method: 'POST', headers: this._headers(), body: JSON.stringify(payload) })
      .then(function(res){ if(!res.ok) return res.text().then(function(t){ throw new Error('checkout failed: ' + res.status + ' ' + t) }); return res.json(); });
  };

  // Expose a default instance and convenience functions for the static prototype
  var defaultClient = new ApiClient('http://127.0.0.1:5000');
  window.BlindDateApi = {
    parseAgent: function(text){ return defaultClient.parseAgent(text); },
    aiDecide: function(preferences, recipient){ return defaultClient.aiDecide({ preferences: preferences, recipient_details: recipient }); },
    doCheckout: function(cartItems, shipping, billing, payment){ return defaultClient.checkout({ cart: { items: cartItems }, shipping_address: shipping, billing_address: billing, payment_method: payment }); },
    setToken: function(t){ defaultClient.setToken(t); }
  };
})();
