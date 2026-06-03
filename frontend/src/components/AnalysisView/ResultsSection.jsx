import { useState } from 'react'
import { EntityCard } from './EntityCard'
import { RiskBadge } from './RiskBadge'
import { ExportButton } from '../ExportButton/ExportButton'

export function ResultsSection({ result }) {
  const [activeTab, setActiveTab] = useState('summary')
  const tabs = ['Summary', 'Entities', 'Risk', 'Raw JSON']

  return (
    <div className="mt-8">

      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-[#111]">
          Analysis results
        </span>
        <div className="flex gap-1.5">
          {[
            `${result.segment_count} segments`,
            `${result.processing_time_ms}ms`,
            result.provider_used,
          ].map(chip => (
            <span key={chip} className="text-[11px] text-[#999] py-[3px] px-2 bg-[#F3F2EE] rounded">{chip}</span>
          ))}
        </div>
      </div>

      <RiskBadge risk={result.risk_analysis} />

      <div className="grid grid-cols-4 gap-2 my-3">
        {[
          { label: 'Loan amount', value: result.entities?.loan_amount?.value ? `₹${Number(result.entities.loan_amount.value).toLocaleString('en-IN')}` : '—', sub: result.entities?.currency?.value || 'INR' },
          { label: 'Interest rate', value: result.entities?.interest_rate?.value ? `${result.entities.interest_rate.value}` : '—', sub: 'per annum' },
          { label: 'Monthly EMI', value: result.entities?.monthly_payment?.value ? `₹${Number(result.entities.monthly_payment.value).toLocaleString('en-IN')}` : '—', sub: `${result.entities?.repayment_duration?.value || '?'} months` },
          { label: 'Total repayment', value: result.financial_summary?.total_repayment ? `₹${Number(result.financial_summary.total_repayment).toLocaleString('en-IN')}` : '—', sub: result.financial_summary?.total_interest ? `₹${Number(result.financial_summary.total_interest).toLocaleString('en-IN')} interest` : '' },
        ].map(stat => (
          <div key={stat.label} className="bg-[#F7F6F2] rounded-[10px] py-[14px] px-4">
            <div className="text-[11px] text-[#999] mb-1">{stat.label}</div>
            <div className="text-[18px] font-semibold text-[#111] tracking-[-0.02em]">{stat.value}</div>
            {stat.sub && <div className="text-[11px] text-[#AAA] mt-[2px]">{stat.sub}</div>}
          </div>
        ))}
      </div>

      <div className="flex gap-0 border-b border-[#E5E5E3] mb-4">
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab.toLowerCase().replace(' ', '_'))}
            className={`py-2 px-[14px] text-[13px] bg-transparent border-none border-b-[1.5px] cursor-pointer -mb-[0.5px] transition-all duration-150 ${
              activeTab === tab.toLowerCase().replace(' ', '_') ? 'text-[#111] font-medium border-[#111]' : 'text-[#999] font-normal border-transparent'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'summary' && (
        <div>
          <div className="bg-white border border-[#E5E5E3] rounded-xl p-5 mb-3">
            <p className="text-sm text-[#444] leading-relaxed">
              {result.summary}
            </p>
          </div>

          {result.math_check && result.financial_summary && (
            <div className={`py-3 px-4 rounded-[10px] text-[13px] mb-3 ${
              result.math_check.warning 
                ? 'bg-[#FFFBEB] border border-[#FDE68A] text-[#92400E]'
                : 'bg-[#F0FDF4] border border-[#86EFAC] text-[#166534]'
            }`}>
              <div className="font-medium mb-2">
                {result.math_check.is_consistent === true ? '✓' : result.math_check.warning ? '⚠' : 'ℹ'} Math Check
              </div>
              <div className="space-y-1 text-[12px] opacity-90">
                <div>Monthly EMI: ₹{result.entities?.monthly_payment?.value?.toLocaleString('en-IN')}</div>
                <div>Loan Tenure: {result.entities?.repayment_duration?.value} months</div>
                <div className="pt-1 border-t border-current/20">
                  <strong>Calculated Total:</strong> ₹{result.entities?.monthly_payment?.value?.toLocaleString('en-IN')} × {result.entities?.repayment_duration?.value} = ₹{result.financial_summary.total_repayment?.toLocaleString('en-IN')}
                </div>
                {result.entities?.total_cost?.value && (
                  <div>
                    <strong>Contract States:</strong> ₹{result.entities.total_cost.value.toLocaleString('en-IN')}
                    {result.math_check.difference_pct > 0 && (
                      <span className="ml-2">({result.math_check.difference_pct}% difference)</span>
                    )}
                  </div>
                )}
              </div>
              {result.math_check.warning && (
                <div className="mt-2 pt-2 border-t border-current/20 font-medium">
                  {result.math_check.warning}
                </div>
              )}
            </div>
          )}

          <ExportButton whatsappText={result.whatsapp_text} />
        </div>
      )}

      {activeTab === 'entities' && (
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(result.entities || {}).map(([key, entity]) => (
            <EntityCard key={key} fieldName={key} entity={entity} />
          ))}
        </div>
      )}

      {activeTab === 'risk' && (
        <div className="bg-white border border-[#E5E5E3] rounded-xl p-5">
          <div className="mb-4">
            <div className="text-[11px] text-[#999] mb-1">Risk score</div>
            <div className={`text-[36px] font-semibold tracking-[-0.03em] ${
              result.risk_analysis?.score >= 7 ? 'text-[#DC2626]' : result.risk_analysis?.score >= 4 ? 'text-[#D97706]' : 'text-[#1D9E75]'
            }`}>
              {result.risk_analysis?.score}
              <span className="text-base text-[#CCC] font-normal">/10</span>
            </div>
          </div>
          {result.risk_analysis?.factors?.length > 0 ? (
            <div className="flex flex-col gap-2">
              {result.risk_analysis.factors.map((f, i) => (
                <div key={i} className="py-2.5 px-3.5 bg-[#FEF9EE] border border-[#FDE68A] rounded-lg text-[13px]">
                  <div className="flex items-start gap-2 text-[#92400E] font-medium">
                    <span className="mt-[1px]">⚠</span>
                    <span>{typeof f === 'string' ? f : f.risk}</span>
                  </div>
                  {typeof f === 'object' && f.recommendation && (
                    <div className="mt-1 ml-5 text-[12px] text-[#B45309]">
                      {f.recommendation}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[13px] text-[#999]">No significant risk factors detected.</p>
          )}
          {result.default_events?.length > 0 && (
            <div className="mt-5">
              <div className="text-xs font-medium text-[#666] mb-2.5">Default triggers</div>
              {result.default_events.map((e, i) => (
                <div key={i} className="py-2.5 px-3.5 bg-[#FEF2F2] border border-[#FECACA] rounded-lg text-[13px] text-[#991B1B] mb-1.5">
                  {e.trigger}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'raw_json' && (
        <div className="bg-[#111] rounded-xl p-5 overflow-auto">
          <pre className="text-xs text-[#A3E635] leading-relaxed m-0 whitespace-pre-wrap">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}