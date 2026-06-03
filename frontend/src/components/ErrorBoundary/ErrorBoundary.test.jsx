/**
 * ErrorBoundary Test Component
 * 
 * This file contains test components to verify ErrorBoundary functionality.
 * To test, temporarily import and use these components in App.jsx.
 */

import { useState } from 'react'

/**
 * Component that throws an error when button is clicked.
 * Use this to test full-page ErrorBoundary.
 */
export function ThrowErrorButton() {
  const [shouldThrow, setShouldThrow] = useState(false)

  if (shouldThrow) {
    throw new Error('Test error: This is a simulated error for testing ErrorBoundary')
  }

  return (
    <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
      <h3 className="font-semibold mb-2">ErrorBoundary Test</h3>
      <p className="text-sm text-gray-600 mb-3">
        Click the button below to simulate an error and test the ErrorBoundary.
      </p>
      <button
        onClick={() => setShouldThrow(true)}
        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        Throw Test Error
      </button>
    </div>
  )
}

/**
 * Component that throws an error on mount.
 * Use this to test section-level ErrorBoundary.
 */
export function BrokenComponent() {
  throw new Error('Test error: This component always throws an error')
}

/**
 * Component that throws an error after a delay.
 * Use this to test async error handling.
 */
export function DelayedErrorComponent() {
  const [shouldThrow, setShouldThrow] = useState(false)

  if (shouldThrow) {
    throw new Error('Test error: Delayed error after 2 seconds')
  }

  // Simulate async operation
  useState(() => {
    setTimeout(() => setShouldThrow(true), 2000)
  }, [])

  return (
    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <p className="text-sm">This component will throw an error in 2 seconds...</p>
    </div>
  )
}

/**
 * Component that throws an error during rendering based on props.
 * Use this to test error recovery.
 */
export function ConditionalErrorComponent({ shouldError }) {
  if (shouldError) {
    throw new Error('Test error: Conditional error based on props')
  }

  return (
    <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
      <p className="text-sm text-green-800">✓ Component rendered successfully</p>
    </div>
  )
}

/**
 * Test harness component with controls.
 * Import this in App.jsx to test all scenarios.
 */
export function ErrorBoundaryTestHarness() {
  const [testMode, setTestMode] = useState('none')

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-4">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">ErrorBoundary Test Harness</h2>
        
        <div className="space-y-2 mb-4">
          <button
            onClick={() => setTestMode('throw')}
            className="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Test 1: Throw Error on Click
          </button>
          
          <button
            onClick={() => setTestMode('broken')}
            className="w-full px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700"
          >
            Test 2: Render Broken Component
          </button>
          
          <button
            onClick={() => setTestMode('delayed')}
            className="w-full px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
          >
            Test 3: Delayed Error (2s)
          </button>
          
          <button
            onClick={() => setTestMode('none')}
            className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Reset
          </button>
        </div>

        <div className="mt-6 p-4 bg-gray-50 rounded">
          {testMode === 'none' && (
            <p className="text-sm text-gray-600">Select a test above</p>
          )}
          {testMode === 'throw' && <ThrowErrorButton />}
          {testMode === 'broken' && <BrokenComponent />}
          {testMode === 'delayed' && <DelayedErrorComponent />}
        </div>
      </div>
    </div>
  )
}

/**
 * USAGE INSTRUCTIONS:
 * 
 * 1. To test full-page ErrorBoundary:
 *    - Import ErrorBoundaryTestHarness in App.jsx
 *    - Add it temporarily to the Main component
 *    - Click "Test 1" or "Test 2" buttons
 *    - Verify ErrorFallback appears with "Try Again" and "Refresh Page" buttons
 *    - Click "Try Again" to verify error recovery
 * 
 * 2. To test section-level ErrorBoundary:
 *    - Wrap ErrorBoundaryTestHarness with ErrorBoundary and SectionErrorFallback
 *    - Click test buttons
 *    - Verify SectionErrorFallback appears (smaller error UI)
 *    - Verify rest of app continues working
 * 
 * 3. To test in production mode:
 *    - Build the app: npm run build
 *    - Serve the build: npm run preview
 *    - Verify error details are hidden in production
 * 
 * Example integration in App.jsx:
 * 
 * import { ErrorBoundaryTestHarness } from './components/ErrorBoundary/ErrorBoundary.test'
 * 
 * function Main() {
 *   return (
 *     <div>
 *       <ErrorBoundaryTestHarness />
 *       {/* rest of your app *\/}
 *     </div>
 *   )
 * }
 */
