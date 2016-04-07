with main as
(Select
   end_time,
  (Select case when sum(acquirer_fee_cents)/-100.0 is null then 0 else sum(acquirer_fee_cents)/-100.0 end FROM dwh_adorable_transaction WHERE type = 'PT' AND mcc_group != 1 and created between start_time and end_time)
  /(select count(1) from dwh_user_activity where activity_type = 1 and activity_end >= end_time and activity_start < end_time) as trxs_rev,
  (SELECT case when sum(available_balance_cents)/100.0*0.089*(-1)/360 is null then 0 else sum(available_balance_cents)/100.0*0.089*(-1)/360 end FROM lr_account_aud
   INNER JOIN lr_risk_model_aud USING (user_created) WHERE available_balance_cents < 0 AND max_overdraft_cents > 0
   AND lr_account_aud.rev_timestamp <= end_time AND lr_account_aud.end_timestamp >= end_time AND lr_risk_model_aud.rev_timestamp <= end_time AND lr_risk_model_aud.end_timestamp >= end_time)
  /(select count(1) from dwh_user_activity where activity_type = 1 and activity_end >= end_time and activity_start < end_time) as overdraft_rev,
  (Select case when sum(case when lr_user_misc.transfer_wise_user_type = 'FULL' then fee_cents*0.7*0.05 else fee_cents*0.7*0.6 end)/100.0 is null then 0 else
   sum(case when lr_user_misc.transfer_wise_user_type = 'FULL' then fee_cents*0.7*0.05 else fee_cents*0.7*0.6 end)/100.0 end from lr_transferwise_details
   INNER JOIN lr_user_misc using (user_created) where created between start_time and end_time and user_certified is not null)
  /(select count(1) from dwh_user_activity where activity_type = 1 and activity_end >= end_time and activity_start < end_time) as transferwise_rev
from dwh_cohort_dates
where end_time between now()- interval '180 day' and now())
select extract(epoch from end_time)*1000 as end_time,
case when lag(trxs_rev) over (order by end_time) <> 0 then 100.0*(trxs_rev - lag(trxs_rev) over (order by end_time))/ lag(trxs_rev) over (order by end_time) else 0 end as trxs_rev,
case when lag(overdraft_rev) over (order by end_time) <> 0 then 100.0*(overdraft_rev - lag(overdraft_rev) over (order by end_time))/ lag(overdraft_rev) over (order by end_time) else 0 end as overdraft_rev,
case when lag(transferwise_rev) over (order by end_time) <> 0 then 100.0*(transferwise_rev - lag(transferwise_rev) over (order by end_time))/ lag(transferwise_rev) over (order by end_time) else 0 end as transferwise_rev
from main
where end_time 
