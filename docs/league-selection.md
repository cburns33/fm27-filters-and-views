# Adapt the pack to your league and save

The same role profile can produce a useful shortlist for one club and an unsuitable list for another. The master files contain statistical floors and positions. Recruitment markets, finances and eligibility belong to your club-specific search.

## What changes between saves

| Factor | What it changes | What to check |
|---|---|---|
| League strength | A given output can be achieved against different opposition. | Compare within the player's competition and position, then scout the step up. |
| Club finances and reputation | Who is affordable and willing to join. | Fees, new wage demands, transfer/loan interest and squad status. |
| Scouting coverage | Which candidates and information are available. | Scouted-players-only and interest switches, unknown values and scouting reach. |
| Database and competition coverage | Which people and usable statistics exist in the save. | Missing or blank data before treating a search as a complete market survey. |
| Season timing | How many minutes candidates have played. | Early/Midseason/Full Season based on their competition's stage. |
| Team style | Opportunities to pass, dribble, defend, press or shoot. | Whether the player's output reflects the role you need. |
| Registration rules | Who can be registered and used. | Work permits, foreign-player limits, homegrown requirements and squad rules in FM. |

A player meeting the floors in the Dutch second division has not demonstrated Premier League quality by meeting the same floors. Equally, a player at a smaller club can be worth scouting. Playing Division selects the player's current market; it does not set an individual quality standard.

## Create a club-specific search

1. Load the relevant league-free role profile.
2. Narrow to the side you need if the profile includes both flanks.
3. Add divisions or nations you want to recruit from and can investigate.
4. Add fees, wages, age and transfer/loan interest settings that fit your club.
5. Check the conditions: eligible divisions should use OR inside their group, while the market group and every core statistic must be required together with AND.
6. Apply the search, use the matching view, and scout promising candidates.
7. Save a working copy named for your club. Preserve the master for a future team or season.

For example, the intended logic is:

```text
Natural at the required position
AND progressive passes/90 >= 3
AND passing >= 80%
AND tackling >= 60%
AND (Playing Division is Market A OR Playing Division is Market B)
```

Check how FM displays the grouping after editing. Loading another preset has not been shown to merge it with the first, so load the role first and add markets to that search. If targeting free agents, check whether a Playing Division restriction excludes unattached players.

## Choose the right season preset

Early has no minute floor. Midseason requires 1,000 minutes; Full Season requires 2,000. These are sample-size gates, not player-quality tiers. The same save date can be early in one competition and late in a calendar-year league.

In the original test save, removing the wing-back minute floor increased the reported results from 2 to 24. This demonstrates sensitivity to that setting in one save, not a general expected result count.

## Adjust floors after checking context

If the search is empty, check minutes, coverage, markets and interest first. If those settings fit your search, relax one statistical requirement at a time and inspect the new candidates. If the pool is too large, apply club constraints before raising every performance floor.

Keep passing completion alongside progression, defensive rates alongside team style, and every per-90 measure alongside minutes. A high completion rate can come from safe passes; defensive totals also reflect opportunities to defend. Use the views to investigate those differences.

Most floors are provisional starting points, not calibrated benchmarks for every league. The [profile guide](profiles.md) records each number and its source. Any custom changes should be saved in your club copy so the master remains a known reference.
