/**
 * CartGenie Background Script
 *
 * Handles communication between the content script and CartGenie backend API.
 * This service worker manages:
 * - Cart data processing and API communication
 * - Analysis result caching and state management
 * - Extension badge updates and user notifications
 * - Error handling and retry logic
 *
 * Architecture:
 * Content Script → Background Script → Django API → AI Agents → Response
 *
 * The background script acts as a bridge, ensuring seamless data flow
 * and providing a responsive user experience across different cart pages.
 */

// Configuration
const API_ENDPOINT = "http://127.0.0.1:8000/api/v1/optimize-cart";

// Global state management - using Maps for better performance and cleanup
let analysisResults = new Map(); // tabId → analysis results
let analysisErrors = new Map(); // tabId → error messages
let loadingStates = new Map(); // tabId → loading status

/**
 * Analyze a shopping cart using CartGenie AI backend
 *
 * This function:
 * 1. Validates cart data and prepares payload
 * 2. Determines user context (country/postal code) from retailer
 * 3. Sends data to Django API for AI processing
 * 4. Manages loading states and error handling
 * 5. Updates extension badge to show results
 *
 * @param {Object} cartData - Cart items and metadata from content script
 * @param {number} tabId - Browser tab ID for state management
 */
async function analyzeCart(cartData, tabId) {
  // Prevent duplicate analysis requests for the same tab
  if (loadingStates.get(tabId)) {
    console.log(`Analysis already in progress for tab ${tabId}`);
    return;
  }

  // Initialize loading state and clear previous results
  loadingStates.set(tabId, true);
  analysisResults.delete(tabId);
  analysisErrors.delete(tabId);

  // Determine user context based on retailer domain
  // TODO: Make this configurable or get from user preferences
  const userContext = {
    country: cartData.sourceRetailer.includes(".in") ? "IN" : "US",
    postalCode: cartData.sourceRetailer.includes(".in") ? "560001" : "90210", // Bangalore / Beverly Hills defaults
  };

  // Prepare API payload according to CartGenie schema
  const payload = {
    userContext: userContext,
    sourceRetailer: cartData.sourceRetailer,
    items: cartData.items,
  };

  try {
    console.log(
      "🚀 Sending cart data to CartGenie API:",
      JSON.stringify(payload, null, 2)
    );

    // Send cart data to Django backend for AI processing
    const response = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
    });

    // Handle HTTP errors
    if (!response.ok) {
      throw new Error(
        `API responded with status: ${response.status} - ${response.statusText}`
      );
    }

    // Parse and store successful results
    const result = await response.json();
    analysisResults.set(tabId, result);

    console.log("✅ Cart analysis completed successfully:", result);

    // Update extension badge to show success
    chrome.action.setBadgeText({ text: "✓", tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#28a745", tabId: tabId });
  } catch (error) {
    console.error("❌ Error during CartGenie API call:", error);

    // Store error for display in popup
    analysisErrors.set(tabId, error.message);

    // Update extension badge to show error
    chrome.action.setBadgeText({ text: "!", tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#dc3545", tabId: tabId });
  } finally {
    loadingStates.set(tabId, false);
  }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "ANALYZE_CART") {
    const tabId = sender.tab?.id;
    if (tabId) {
      analyzeCart(request.payload, tabId);

      // Show loading badge
      chrome.action.setBadgeText({ text: "...", tabId: tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#ff007f", tabId: tabId });
    }
  } else if (request.type === "GET_ANALYSIS_RESULT") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tabId = tabs[0]?.id;
      if (tabId) {
        sendResponse({
          isLoading: loadingStates.get(tabId) || false,
          result: analysisResults.get(tabId),
          error: analysisErrors.get(tabId),
        });
      } else {
        sendResponse({
          isLoading: false,
          result: null,
          error: "No active tab",
        });
      }
    });
  }
  return true; // Required for async sendResponse
});

// Clear badge when tab is updated
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete") {
    chrome.action.setBadgeText({ text: "", tabId: tabId });
  }
});
