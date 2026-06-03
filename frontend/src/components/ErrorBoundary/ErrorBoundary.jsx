import { Component } from 'react'
import ErrorFallback from './ErrorFallback'

/**
 * ErrorBoundary component to catch JavaScript errors in child components.
 * 
 * This prevents the entire app from crashing when a component throws an error.
 * Instead, it shows a fallback UI and allows recovery without page refresh.
 * 
 * Usage:
 *   <ErrorBoundary>
 *     <YourComponent />
 *   </ErrorBoundary>
 * 
 * With custom fallback:
 *   <ErrorBoundary fallback={<CustomError />}>
 *     <YourComponent />
 *   </ErrorBoundary>
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  /**
   * Update state when an error is caught.
   * This is called during the render phase.
   */
  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      error,
    }
  }

  /**
   * Log error details after error is caught.
   * This is called during the commit phase.
   */
  componentDidCatch(error, errorInfo) {
    // Log to console in development
    console.error('ErrorBoundary caught an error:', error)
    console.error('Error info:', errorInfo)

    // Store error info for display
    this.setState({ errorInfo })

    // TODO: Send to error tracking service (Sentry, LogRocket, etc.)
    // Example:
    // if (import.meta.env.PROD) {
    //   Sentry.captureException(error, { extra: errorInfo })
    // }
  }

  /**
   * Reset error state to allow recovery without page refresh.
   */
  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided, otherwise use default
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <ErrorFallback
          error={this.state.error}
          errorInfo={this.state.errorInfo}
          resetError={this.resetError}
        />
      )
    }

    // No error, render children normally
    return this.props.children
  }
}

export default ErrorBoundary
