/**
 * CartGenie Content Script
 *
 * This script handles cart detection and item extraction across multiple e-commerce platforms.
 * It automatically detects supported shopping cart pages and provides a seamless interface
 * for users to optimize their cart contents using AI-powered price comparison.
 *
 * Supported Platforms:
 * - Amazon India (.amazon.in)
 * - Flipkart (.flipkart.com)
 * - BigBasket (.bigbasket.com)
 * - Swiggy Instamart (.swiggy.com/instamart)
 *
 * Architecture:
 * - Platform Detection: Identifies current retailer and cart page
 * - UI Injection: Adds CartGenie button to cart interfaces
 * - Data Extraction: Parses cart items using platform-specific selectors
 * - Communication: Sends cart data to background script for API processing
 */

class CartGenieContent {
  constructor() {
    this.isInitialized = false;
    this.currentPlatform = null;
    this.retryCount = 0;
    this.maxRetries = 5;
    this.extractedItems = []; // Cache for extracted cart items
  }

  /**
   * Initialize the content script and start cart detection
   *
   * This method:
   * 1. Detects the current e-commerce platform
   * 2. Verifies we're on a supported cart page
   * 3. Injects the CartGenie UI elements
   * 4. Sets up event listeners for user interactions
   */
  async init() {
    if (this.isInitialized) return;

    try {
      this.log("Initializing CartGenie content script...");

      // Step 1: Detect the current platform
      this.detectPlatform();

      if (!this.currentPlatform) {
        this.log(
          "No supported platform detected - CartGenie not available on this page"
        );
        return;
      }

      this.log(`✓ Detected platform: ${this.currentPlatform.name}`);

      // Step 2: Wait for page to be ready and inject UI
      this.waitForPageAndInject();

      this.isInitialized = true;
      this.log("✓ CartGenie initialized successfully");
    } catch (error) {
      console.error("❌ CartGenie initialization error:", error);
    }
  }

  /**
   * Detect the current e-commerce platform and configure selectors
   *
   * Uses URL patterns and hostname matching to identify supported platforms.
   * Each platform has specific CSS selectors for extracting cart item data.
   *
   * Platform Configuration:
   * - name: Display name for the platform
   * - id: Unique identifier for the platform
   * - color: Brand color for UI elements
   * - selectors: CSS selectors for cart items, titles, and prices
   */
  detectPlatform() {
    const url = window.location.href;
    const hostname = window.location.hostname;

    // Amazon Detection (India and other domains)
    if (hostname.includes("amazon")) {
      if (url.includes("/gp/cart") || url.includes("/cart")) {
        this.currentPlatform = {
          name: "Amazon",
          id: "amazon",
          color: "#ff9900",
          selectors: {
            container:
              "[data-name='Active Items'] [data-item-index], .sc-list-item-content, #sc-active-cart .sc-list-item",
            title:
              "[data-cy='item-title'] span, .sc-product-title span, .sc-product-title a",
            price:
              ".sc-product-price .a-offscreen, .sc-product-price .sc-price, .a-price .a-offscreen",
          },
        };
      }
    } else if (hostname.includes("flipkart")) {
      if (url.includes("/viewcart") || url.includes("/cart")) {
        this.currentPlatform = {
          name: "Flipkart",
          id: "flipkart",
          color: "#2874f0",
          selectors: {
            container: "._1fragrcH, .sBxzFz",
            title: "._2-4G_o a, .sBxzFz a, ._3I9Jbp",
            price: "._30jeq3._16Jk6d, ._30jeq3._1_bKsh, .WMgn0j",
          },
        };
      }
    } else if (hostname.includes("bigbasket")) {
      if (url.includes("/basket") || url.includes("/cart")) {
        this.currentPlatform = {
          name: "BigBasket",
          id: "bigbasket",
          color: "#84c225",
          selectors: {
            container: ".CartItemCard___StyledDiv-sc-1hz2rfp-0, .basket-item",
            title: ".CartItemCard___StyledDiv2-sc-1hz2rfp-1 a, .product-name a",
            price: ".CartItemCard___StyledDiv8-sc-1hz2rfp-7, .discnt-price",
          },
        };
      }
    } else if (hostname.includes("swiggy")) {
      if (url.includes("/instamart") && url.includes("/cart")) {
        this.currentPlatform = {
          name: "Swiggy Instamart",
          id: "swiggy",
          color: "#fc8019",
          selectors: {
            container: ".CartItem, [class*='CartItem']",
            title: ".CartItem h4, [class*='CartItem'] h4, [class*='Name']",
            price:
              ".CartItem [class*='Price'], [class*='CartItem'] [class*='Price']",
          },
        };
      }
    } else if (hostname.includes("walmart")) {
      if (url.includes("/cart")) {
        this.currentPlatform = {
          name: "Walmart",
          id: "walmart",
          color: "#0071ce",
          selectors: {
            container: "[data-automation-id='cart-line-item'], .cart-item",
            title:
              "[data-automation-id='product-title'] a, .product-title-link",
            price: "[itemprop='price'], .price-current",
          },
        };
      }
    } else if (hostname.includes("target")) {
      if (url.includes("/cart")) {
        this.currentPlatform = {
          name: "Target",
          id: "target",
          color: "#cc0000",
          selectors: {
            container: "[data-test='cartItem'], .cart-item",
            title: "[data-test='product-title'] a, .product-title",
            price: "[data-test='product-price'], .price",
          },
        };
      }
    }
  }

  /**
   * Wait for page elements and inject the analyze button
   */
  waitForPageAndInject() {
    if (this.retryCount >= this.maxRetries) {
      this.log("Max retries reached, giving up");
      return;
    }

    const success = this.tryInjectButton();
    if (success) {
      this.log("Button injected successfully");
      return;
    }

    this.retryCount++;
    this.log(`Retry ${this.retryCount}/${this.maxRetries} in 1 second...`);

    setTimeout(() => {
      this.waitForPageAndInject();
    }, 1000);
  }

  /**
   * Try to inject the analyze button
   */
  tryInjectButton() {
    try {
      // Check if button already exists
      if (document.querySelector(".cartgenie-analyze-btn")) {
        return true;
      }

      // Try to find a good spot to inject the button
      const targets = [
        "form[action*='cart']",
        ".cart-container",
        ".cart-content",
        "#cart",
        "[id*='cart']",
        "[class*='cart']",
      ];

      let targetElement = null;
      for (const selector of targets) {
        targetElement = document.querySelector(selector);
        if (targetElement) break;
      }

      if (!targetElement) {
        // Fallback to body
        targetElement = document.body;
      }

      const button = this.createAnalyzeButton();
      targetElement.appendChild(button);

      return true;
    } catch (error) {
      this.log(`Button injection failed: ${error.message}`);
      return false;
    }
  }

  /**
   * Create the analyze button
   */
  createAnalyzeButton() {
    const button = document.createElement("button");
    button.className = "cartgenie-analyze-btn";
    button.innerHTML = `
      <span style="margin-right: 8px;">🔍</span>
      Find Better Prices with CartGenie
    `;

    // Style the button
    Object.assign(button.style, {
      position: "fixed",
      bottom: "20px",
      right: "20px",
      zIndex: "9999",
      padding: "15px 25px",
      backgroundColor: this.currentPlatform.color,
      color: "white",
      border: "none",
      borderRadius: "8px",
      cursor: "pointer",
      fontSize: "16px",
      fontWeight: "bold",
      boxShadow: "0 4px 15px rgba(0,0,0,0.3)",
      transition: "all 0.3s ease",
    });

    // Add hover effects
    button.addEventListener("mouseenter", () => {
      button.style.transform = "translateY(-2px)";
      button.style.boxShadow = "0 6px 20px rgba(0,0,0,0.4)";
    });

    button.addEventListener("mouseleave", () => {
      button.style.transform = "translateY(0)";
      button.style.boxShadow = "0 4px 15px rgba(0,0,0,0.3)";
    });

    // Add click handler
    button.addEventListener("click", () => {
      this.handleAnalyzeClick(button);
    });

    return button;
  }

  /**
   * Handle analyze button click
   */
  async handleAnalyzeClick(button) {
    try {
      // Update button to show loading state
      button.innerHTML = `
        <span style="margin-right: 8px;">⏳</span>
        Analyzing Cart...
      `;
      button.disabled = true;
      button.style.backgroundColor = "#666";

      // Scrape cart items
      const items = this.scrapeCartItems();

      if (!items || items.length === 0) {
        this.showNotification("No items found in cart", "error");
        return;
      }

      this.log(`Found ${items.length} items in cart`);

      // Send to background script
      chrome.runtime.sendMessage({
        type: "ANALYZE_CART",
        payload: {
          sourceRetailer: window.location.hostname,
          items: items,
        },
      });

      this.showNotification(`Analyzing ${items.length} items...`, "info");
    } catch (error) {
      this.log(`Analysis failed: ${error.message}`);
      this.showNotification("Analysis failed. Please try again.", "error");
    } finally {
      // Reset button
      setTimeout(() => {
        button.innerHTML = `
          <span style="margin-right: 8px;">🔍</span>
          Find Better Prices with CartGenie
        `;
        button.disabled = false;
        button.style.backgroundColor = this.currentPlatform.color;
      }, 2000);
    }
  }

  /**
   * Scrape cart items from the page
   */
  scrapeCartItems() {
    this.log("Starting cart scrape...");
    const items = [];

    if (!this.currentPlatform?.selectors) {
      this.log("No selectors defined for platform");
      return items;
    }

    const containers = document.querySelectorAll(
      this.currentPlatform.selectors.container
    );
    this.log(`Found ${containers.length} potential item containers`);

    containers.forEach((container, index) => {
      try {
        const titleElement = container.querySelector(
          this.currentPlatform.selectors.title
        );
        const priceElement = container.querySelector(
          this.currentPlatform.selectors.price
        );

        if (!titleElement || !priceElement) {
          this.log(`Item ${index + 1}: Missing title or price element`);
          return;
        }

        const productTitle = titleElement.textContent?.trim();
        const priceText = priceElement.textContent
          ?.replace(/[₹$,\s]/g, "")
          .trim();
        const price = parseFloat(priceText);

        if (productTitle && !isNaN(price) && price > 0) {
          items.push({
            productTitle,
            price,
            quantity: 1,
            currency: this.detectCurrency(),
          });
          this.log(`Item ${index + 1}: ${productTitle} - ${price}`);
        } else {
          this.log(
            `Item ${
              index + 1
            }: Invalid data - title: "${productTitle}", price: "${priceText}"`
          );
        }
      } catch (error) {
        this.log(`Error processing item ${index + 1}: ${error.message}`);
      }
    });

    this.log(`Successfully scraped ${items.length} items`);
    return items;
  }

  /**
   * Detect currency based on location
   */
  detectCurrency() {
    const hostname = window.location.hostname;
    if (hostname.includes(".in")) {
      return "INR";
    }
    return "USD";
  }

  /**
   * Show notification to user
   */
  showNotification(message, type = "info") {
    const notification = document.createElement("div");
    notification.className = "cartgenie-notification";
    notification.textContent = message;

    const colors = {
      info: "#007bff",
      success: "#28a745",
      error: "#dc3545",
    };

    Object.assign(notification.style, {
      position: "fixed",
      top: "20px",
      right: "20px",
      zIndex: "10000",
      padding: "12px 20px",
      backgroundColor: colors[type],
      color: "white",
      borderRadius: "6px",
      fontSize: "14px",
      boxShadow: "0 4px 15px rgba(0,0,0,0.3)",
    });

    document.body.appendChild(notification);

    // Auto remove after 3 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 3000);
  }

  /**
   * Logging utility
   */
  log(message) {
    console.log(
      `%cCartGenie:%c ${message}`,
      "font-weight: bold; color: #ff007f;",
      "color: default;"
    );
  }
}

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    new CartGenieContent().init();
  });
} else {
  new CartGenieContent().init();
}
