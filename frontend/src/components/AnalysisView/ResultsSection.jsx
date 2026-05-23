import { useState } from 'react'
import { EntityCard } from './EntityCard'
import { RiskBadge } from './RiskBadge'
import { ExportButton } from '../ExportButton/ExportButton'

export function ResultsSection({ result }) {
  const [activeTab, setActiveTab] = useState('summary')
  const tabs = ['Summary', 'Entities', 'Risk', 'Raw JSON']

  return (
    <div style={{ marginTop: '32px' }}>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
      }}>
        <span style={{ fontSize: '14px', fontWeight: '500', color: '#111' }}>
          Analysis results
        </span>
        <div style={{ display: 'flex', gap: '6px' }}>
          {[
            `${result.segment_count} segments`,
            `${result.processing_time_ms}ms`,
            result.provider_used,
          ].map(chip => (
            <span key={chip} style={{
              fontSize: '11px', color: '#999',
              padding: '3px 8px',
              background: '#F3F2EE',
              borderRadius: '4px',
            }}>{chip}</span>
          ))}
        </div>
      </div>

      <RiskBadge risk={result.risk_analysis} />

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '8px',
        margin: '12px 0',
      }}>
        {[
          { label: 'Loan amount', value: result.entities?.loan_amount?.value ? `₹${Number(result.entities.loan_amount.value).toLocaleString('en-IN')}` : '—', sub: result.entities?.currency?.value || 'INR' },
          { label: 'Interest rate', value: result.entities?.interest_rate?.value ? `${result.entities.interest_rate.value}` : '—', sub: 'per annum' },
          { label: 'Monthly EMI', value: result.entities?.monthly_payment?.value ? `₹${Number(result.entities.monthly_payment.value).toLocaleString('en-IN')}` : '—', sub: `${result.entities?.repayment_duration?.value || '?'} months` },
          { label: 'Total repayment', value: result.financial_summary?.total_repayment ? `₹${Number(result.financial_summary.total_repayment).toLocaleString('en-IN')}` : '—', sub: result.financial_summary?.total_interest ? `₹${Number(result.financial_summary.total_interest).toLocaleString('en-IN')} interest` : '' },
        ].map(stat => (
          <div key={stat.label} style={{
            background: '#F7F6F2',
            borderRadius: '10px',
            padding: '14px 16px',
          }}>
            <div style={{ fontSize: '11px', color: '#999', marginBottom: '4px' }}>{stat.label}</div>
            <div style={{ fontSize: '18px', fontWeight: '600', color: '#111', letterSpacing: '-0.02em' }}>{stat.value}</div>
            {stat.sub && <div style={{ fontSize: '11px', color: '#AAA', marginTop: '2px' }}>{stat.sub}</div>}
          </div>
        ))}
      </div>

      <div style={{
        display: 'flex',
        gap: '0',
        borderBottom: '0.5px solid #E5E5E3',
        marginBottom: '16px',
      }}>
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab.toLowerCase().replace(' ', '_'))}
            style={{
              padding: '8px 14px',
              fontSize: '13px',
              color: activeTab === tab.toLowerCase().replace(' ', '_') ? '#111' : '#999',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === tab.toLowerCase().replace(' ', '_') ? '1.5px solid #111' : '1.5px solid transparent',
              cursor: 'pointer',
              fontWeight: activeTab === tab.toLowerCase().replace(' ', '_') ? '500' : '400',
              marginBottom: '-0.5px',
              transition: 'all 0.15s',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'summary' && (
        <div>
          <div style={{
            background: '#fff',
            border: '0.5px solid #E5E5E3',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '12px',
          }}>
            <p style={{ fontSize: '14px', color: '#444', lineHeight: '1.8' }}>
              {result.summary}
            </p>
          </div>

          {result.math_check?.warning && (
            <div style={{
              padding: '12px 16px',
              background: '#FFFBEB',
              border: '0.5px solid #FDE68A',
              borderRadius: '10px',
              fontSize: '13px',
              color: '#92400E',
              marginBottom: '12px',
            }}>
              ⚠ {result.math_check.warning}
            </div>
          )}

          <ExportButton whatsappText={result.whatsapp_text} />
        </div>
      )}

      {activeTab === 'entities' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          {Object.entries(result.entities || {}).map(([key, entity]) => (
            <EntityCard key={key} fieldName={key} entity={entity} />
          ))}
        </div>
      )}

      {activeTab === 'risk' && (
        <div style={{
          background: '#fff',
          border: '0.5px solid #E5E5E3',
          borderRadius: '12px',
          padding: '20px',
        }}>
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '11px', color: '#999', marginBottom: '4px' }}>Risk score</div>
            <div style={{ fontSize: '36px', fontWeight: '600', letterSpacing: '-0.03em', color: result.risk_analysis?.score >= 7 ? '#DC2626' : result.risk_analysis?.score >= 4 ? '#D97706' : '#1D9E75' }}>
              {result.risk_analysis?.score}
              <span style={{ fontSize: '16px', color: '#CCC', fontWeight: '400' }}>/10</span>
            </div>
          </div>
          {result.risk_analysis?.factors?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {result.risk_analysis.factors.map((f, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: '10px',
                  padding: '10px 14px',
                  background: '#FEF9EE',
                  borderRadius: '8px',
                  fontSize: '13px', color: '#92400E',
                }}>
                  <span>⚠</span> {f}
                </div>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: '13px', color: '#999' }}>No significant risk factors detected.</p>
          )}
          {result.default_events?.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <div style={{ fontSize: '12px', fontWeight: '500', color: '#666', marginBottom: '10px' }}>Default triggers</div>
              {result.default_events.map((e, i) => (
                <div key={i} style={{
                  padding: '10px 14px',
                  background: '#FEF2F2',
                  border: '0.5px solid #FECACA',
                  borderRadius: '8px',
                  fontSize: '13px', color: '#991B1B',
                  marginBottom: '6px',
                }}>
                  {e.trigger}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'raw_json' && (
        <div style={{
          background: '#111',
          borderRadius: '12px',
          padding: '20px',
          overflow: 'auto',
        }}>
          <pre style={{
            fontSize: '12px',
            color: '#A3E635',
            lineHeight: '1.6',
            margin: '0',
            whiteSpace: 'pre-wrap',
          }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}