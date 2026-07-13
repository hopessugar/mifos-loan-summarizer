import { useState } from 'react'
import { EntityCard } from './EntityCard'
import { RiskBadge } from './RiskBadge'
import { ExportButton } from '../ExportButton/ExportButton'
import { useTranslation } from '../../hooks/useTranslation'
import { formatCurrency } from '../../utils/currencyUtils'

export function ResultsSection({ result }) {
  const [activeTab, setActiveTab] = useState('summary')
  const { t } = useTranslation()
  const currency = result.entities?.currency?.value || null

  const tabs = [
    { key: 'summary', label: t('results.tab.summary') },
    { key: 'entities', label: t('results.tab.entities') },
    { key: 'risk', label: t('results.tab.risk') },
    { key: 'raw_json', label: t('results.tab.rawJson') },
  ]

  return (
    <div className="mt-8">

      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium text-[#111]">
          {t('results.title')}
        </span>
        <div className="flex gap-1.5">
          {[
            t('results.segments', { n: result.segment_count }),
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
          { label: t('stat.loanAmount'), value: result.entities?.loan_amount?.value ? formatCurrency(result.entities.loan_amount.value, currency) : '—', sub: currency || '—' },
          { label: t('stat.interestRate'), value: result.entities?.interest_rate?.value ? `${result.entities.interest_rate.value}` : '—', sub: t('stat.perAnnum') },
          { label: t('stat.monthlyEmi'), value: result.entities?.monthly_payment?.value ? formatCurrency(result.entities.monthly_payment.value, currency) : '—', sub: t('stat.months', { n: result.entities?.repayment_duration?.value || '?' }) },
          { label: t('stat.totalRepayment'), value: result.financial_summary?.total_repayment ? formatCurrency(result.financial_summary.total_repayment, currency) : '—', sub: result.financial_summary?.total_interest ? t('stat.interest', { amount: formatCurrency(result.financial_summary.total_interest, currency) }) : '' },
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
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`py-2 px-[14px] text-[13px] bg-transparent border-none border-b-[1.5px] cursor-pointer -mb-[0.5px] transition-all duration-150 ${
              activeTab === tab.key ? 'text-[#111] font-medium border-[#111]' : 'text-[#999] font-normal border-transparent'
            }`}
          >
            {tab.label}
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
                {result.math_check.is_consistent === true ? '✓' : result.math_check.warning ? '⚠' : 'ℹ'} {t('math.label')}
              </div>
              <div className="space-y-1 text-[12px] opacity-90">
                <div>{t('math.monthlyEmi')} {formatCurrency(result.entities?.monthly_payment?.value, currency)}</div>
                <div>{t('math.tenure')} {t('math.tenureMonths', { n: result.entities?.repayment_duration?.value })}</div>
                <div className="pt-1 border-t border-current/20">
                  <strong>{t('math.calcTotal')}</strong> {formatCurrency(result.entities?.monthly_payment?.value, currency)} × {result.entities?.repayment_duration?.value} = {formatCurrency(result.financial_summary.total_repayment, currency)}
                </div>
                {result.entities?.total_cost?.value && (
                  <div>
                    <strong>{t('math.contractStates')}</strong> {formatCurrency(result.entities.total_cost.value, currency)}
                    {result.math_check.difference_pct > 0 && (
                      <span className="ml-2">({t('math.difference', { pct: result.math_check.difference_pct })})</span>
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
            <div className="text-[11px] text-[#999] mb-1">{t('risk.scoreLabel')}</div>
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
            <p className="text-[13px] text-[#999]">{t('risk.noFactors')}</p>
          )}
          {result.default_events?.length > 0 && (
            <div className="mt-5">
              <div className="text-xs font-medium text-[#666] mb-2.5">{t('risk.defaultTriggers')}</div>
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