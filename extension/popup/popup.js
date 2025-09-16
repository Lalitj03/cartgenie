/**
 * CartGenie Popup Script
 * Handles the extension popup interface
 */

class CartGeniePopup {
  constructor() {
    this.contentContainer = document.getElementById("content-container");
    this.currentTab = null;
  }

  async init() {
    try {
      // Get current tab
      this.currentTab = await this.getCurrentTab();

      // Check if we're on a supported cart page
      const isCartPage = this.isCartPage();

      if (!isCartPage) {
        this.renderNotCartPage();
        return;
      }

      // Show loading initially
      this.renderLoading();

      // Get analysis results
      this.getAnalysisResults();
    } catch (error) {
      console.error("CartGenie Popup: Initialization error:", error);
      this.renderError("Failed to initialize popup");
    }
  }

  async getCurrentTab() {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });
    return tab;
  }

  isCartPage() {
    if (!this.currentTab?.url) return false;

    const url = this.currentTab.url;
    const cartPatterns = [
      "/cart",
      "/gp/cart",
      "/viewcart",
      "/basket",
      "/checkout/cart",
    ];

    return cartPatterns.some((pattern) => url.includes(pattern));
  }

  getAnalysisResults() {
    chrome.runtime.sendMessage({ type: "GET_ANALYSIS_RESULT" }, (response) => {
      if (chrome.runtime.lastError) {
        this.renderError(
          `Connection Error: ${chrome.runtime.lastError.message}`
        );
        return;
      }

      if (response.isLoading) {
        this.renderLoading();
      } else if (response.error) {
        this.renderError(response.error);
      } else if (response.result) {
        this.renderResults(response.result);
      } else {
        this.renderNoAnalysis();
      }
    });
  }

  renderLoading() {
    this.contentContainer.innerHTML = `
      <div class="loading-state">
        <div class="loader"></div>
        <p>Analyzing your cart for the best deals...</p>
        <small style="color: #666; margin-top: 10px; display: block;">
          This may take a few moments while we compare prices across retailers.
        </small>
      </div>
    `;
  }

  renderError(errorMessage) {
    this.contentContainer.innerHTML = `
      <div class="error-state">
        <div style="font-size: 24px; margin-bottom: 10px;">⚠️</div>
        <h3>Oops! Something went wrong.</h3>
        <p>${errorMessage || "Could not complete the analysis."}</p>
        <button onclick="window.close()" style="margin-top: 15px; padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
          Close
        </button>
      </div>
    `;
  }

  renderNotCartPage() {
    this.contentContainer.innerHTML = `
      <div class="container">
        <div style="text-align: center; padding: 20px;">
          <div style="font-size: 48px; margin-bottom: 15px;">🛒</div>
          <h3>Navigate to Your Cart</h3>
          <p style="color: #666; margin: 15px 0;">
            CartGenie works on cart pages. Please navigate to your shopping cart on any supported retailer:
          </p>
          <div style="text-align: left; margin: 20px 0;">
            <strong>Supported Retailers:</strong>
            <ul style="margin: 10px 0; padding-left: 20px; color: #666;">
              <li>Amazon (US & India)</li>
              <li>Flipkart</li>
              <li>BigBasket</li>
              <li>Swiggy Instamart</li>
              <li>Walmart</li>
              <li>Target</li>
            </ul>
          </div>
          <p style="font-size: 12px; color: #999;">
            Once you're on a cart page, look for the "Find Better Prices" button to start analyzing!
          </p>
        </div>
      </div>
    `;
  }

  renderNoAnalysis() {
    this.contentContainer.innerHTML = `
      <div class="container">
        <div style="text-align: center; padding: 20px;">
          <div style="font-size: 48px; margin-bottom: 15px;">🔍</div>
          <h3>Ready to Find Better Prices?</h3>
          <p style="color: #666; margin: 15px 0;">
            Click the "Find Better Prices" button on the cart page to start analyzing your items.
          </p>
          <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; margin: 15px 0;">
            <small style="color: #666;">
              💡 <strong>Tip:</strong> Look for the floating button at the bottom right of the cart page.
            </small>
          </div>
        </div>
      </div>
    `;
  }

  renderResults(resultData) {
    if (!resultData) {
      this.renderError("No analysis data was found.");
      return;
    }

    // Handle case where API returns different structure
    const recommendations = resultData.recommendations || [];
    const totalSavings = resultData.totalSavings || 0;
    const originalTotal = resultData.originalTotal || 0;
    const optimizedTotal = resultData.optimizedTotal || 0;

    const formatCurrency = (amount) => {
      if (typeof amount !== "number") return "0.00";
      return amount.toFixed(2);
    };

    // Use a placeholder currency if not provided
    const currencySymbol = resultData.currency || "$";

    let recommendationsHTML = "";

    if (recommendations.length > 0) {
      recommendationsHTML = recommendations
        .map(
          (rec) => `
        <div class="recommendation">
          <div class="item-title">${
            rec.originalItem?.productTitle || "Product"
          }</div>
          <div style="margin: 5px 0;">
            <span class="original-price">
              ${rec.originalItem?.currency || currencySymbol} ${formatCurrency(
            rec.originalItem?.price
          )}
            </span>
            <span style="margin: 0 5px;">→</span>
            <span class="new-price">
              ${
                rec.cheapestAlternative?.currency || currencySymbol
              } ${formatCurrency(rec.cheapestAlternative?.price)}
            </span>
          </div>
          <div style="margin-top: 8px;">
            <a href="${
              rec.cheapestAlternative?.url || "#"
            }" target="_blank" class="retailer-link">
              View at ${rec.cheapestAlternative?.retailer || "Retailer"}
            </a>
          </div>
        </div>
      `
        )
        .join("");
    } else {
      recommendationsHTML = `
        <div style="text-align: center; padding: 20px;">
          <div style="font-size: 32px; margin-bottom: 10px;">🎉</div>
          <h3 style="color: #28a745; margin-bottom: 10px;">Great Job!</h3>
          <p>You already have the best prices for these items!</p>
        </div>
      `;
    }

    const savingsDisplay =
      totalSavings > 0
        ? `
      <div class="results-summary">
        <div class="savings">
          You can save ${currencySymbol}${formatCurrency(totalSavings)}!
        </div>
        <div class="details">
          Original Total: ${currencySymbol}${formatCurrency(originalTotal)} • 
          New Total: ${currencySymbol}${formatCurrency(optimizedTotal)}
        </div>
      </div>
    `
        : "";

    this.contentContainer.innerHTML = `
      ${savingsDisplay}
      <div class="container">
        ${recommendationsHTML}
      </div>
      <div style="text-align: center; margin-top: 15px; padding: 10px;">
        <button onclick="location.reload()" style="padding: 8px 16px; background: #ff007f; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">
          Refresh Results
        </button>
      </div>
    `;
  }
}

// Initialize popup when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new CartGeniePopup().init();
});
