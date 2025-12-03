#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reply Pattern Analyzer - Love Score & Relationship Metrics
Analyzes reply times, conversation patterns, and relationship dynamics
Inspired by WhatsApp Reply Analyzer
"""

import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
import math

class ReplyPoint:
    """Represents a single reply data point"""
    def __init__(self, index: int, reply_time_minutes: float):
        self.x = index  # Reply number for this person
        self.y = reply_time_minutes  # Time to reply in minutes

class RegressionResult:
    """Linear regression results"""
    def __init__(self, slope: float, intercept: float, r: float, r2: float):
        self.slope = slope
        self.intercept = intercept
        self.r = r  # Correlation coefficient
        self.r2 = r2  # R-squared value

class ParticipantStats:
    """Statistics for a participant's replies"""
    def __init__(self, count: int, median: float, mean: float, std: float, fast_rate: float):
        self.count = count
        self.median = median
        self.mean = mean
        self.std = std
        self.fast_rate = fast_rate  # Percentage of replies within 5 minutes

class LoveScore:
    """Love score calculation result"""
    def __init__(self, score: int, verdict: str, breakdown: Dict[str, float]):
        self.score = score  # 0-100
        self.verdict = verdict
        self.breakdown = breakdown

class ReplyAnalyzer:
    """
    Analyzes reply patterns between two participants
    Calculates "Love Score" based on:
    - Reply speed trends (negative slope = getting faster over time)
    - Median reply time
    - Fast reply rate (% of replies within 5 minutes)
    - Consistency (standard deviation)
    """
    
    def __init__(self, messages: List):
        self.messages = messages
        
    def build_reply_series(self, target: str, counterpart: str) -> Tuple[List[ReplyPoint], List[ReplyPoint]]:
        """
        Build reply time series for both participants
        Returns: (target_series, counterpart_series)
        """
        target_series = []
        counterpart_series = []
        target_index = 0
        counterpart_index = 0
        
        for i in range(1, len(self.messages)):
            prev = self.messages[i - 1]
            curr = self.messages[i]
            
            # Skip if same person sent consecutive messages
            if not hasattr(prev, 'sender') or not hasattr(curr, 'sender'):
                continue
            if prev.sender == curr.sender:
                continue
            if not hasattr(prev, 'timestamp') or not hasattr(curr, 'timestamp'):
                continue
                
            # Calculate reply time in minutes
            time_diff = curr.timestamp - prev.timestamp
            delta_minutes = time_diff.total_seconds() / 60
            
            # Track replies
            if curr.sender == target and prev.sender == counterpart:
                target_index += 1
                target_series.append(ReplyPoint(target_index, delta_minutes))
            elif curr.sender == counterpart and prev.sender == target:
                counterpart_index += 1
                counterpart_series.append(ReplyPoint(counterpart_index, delta_minutes))
        
        return target_series, counterpart_series
    
    def compute_regression(self, points: List[ReplyPoint]) -> RegressionResult:
        """Compute linear regression on reply points"""
        n = len(points)
        
        if n < 2:
            avg_y = statistics.mean([p.y for p in points]) if points else 0
            return RegressionResult(slope=0, intercept=avg_y, r=0, r2=0)
        
        sum_x = sum(p.x for p in points)
        sum_y = sum(p.y for p in points)
        sum_xy = sum(p.x * p.y for p in points)
        sum_xx = sum(p.x * p.x for p in points)
        sum_yy = sum(p.y * p.y for p in points)
        
        # Calculate slope and intercept
        num = n * sum_xy - sum_x * sum_y
        den = n * sum_xx - sum_x * sum_x
        slope = num / den if den != 0 else 0
        intercept = sum_y / n - slope * (sum_x / n)
        
        # Calculate correlation coefficient
        r_den = math.sqrt((n * sum_xx - sum_x * sum_x) * (n * sum_yy - sum_y * sum_y))
        r = num / r_den if r_den != 0 else 0
        r2 = r * r
        
        return RegressionResult(slope, intercept, r, r2)
    
    def compute_stats(self, points: List[ReplyPoint]) -> ParticipantStats:
        """Compute statistics for reply times"""
        y_values = [p.y for p in points]
        count = len(y_values)
        
        if count == 0:
            return ParticipantStats(0, 0, 0, 0, 0)
        
        median = statistics.median(y_values)
        mean = statistics.mean(y_values)
        std = statistics.stdev(y_values) if count > 1 else 0
        fast_rate = len([v for v in y_values if v <= 5]) / count if count > 0 else 0
        
        return ParticipantStats(count, median, mean, std, fast_rate)
    
    def clamp01(self, value: float) -> float:
        """Clamp value between 0 and 1"""
        return max(0, min(1, value))
    
    def calculate_love_score(self, target_series: List[ReplyPoint], 
                            target_regression: RegressionResult,
                            target_stats: ParticipantStats) -> LoveScore:
        """
        Calculate Love Score (0-100) based on reply patterns
        
        Score components:
        - Slope (35%): Negative slope = getting faster over time (good!)
        - Median reply time (35%): Lower is better
        - Fast reply rate (20%): Higher % of <5min replies is better
        - Consistency (10%): Lower std deviation is better
        """
        if len(target_series) == 0:
            return LoveScore(0, "Insufficient data", {})
        
        slope = target_regression.slope
        # Negative slope is better (getting faster over time)
        # Scale by 0.5 minutes per message
        slope_scaled = self.clamp01(-slope / 0.5)
        
        # Median reply time - closer to 0 is better, cap at 120 minutes
        median = target_stats.median
        median_scaled = self.clamp01((120 - min(median, 120)) / 120)
        
        # Fast reply rate (already 0-1)
        fast_rate = target_stats.fast_rate
        
        # Consistency - lower std deviation is better, cap at 60
        std = target_stats.std
        consistency = self.clamp01(1 - min(std, 60) / 60)
        
        # Weighted score
        score = 100 * (
            0.35 * slope_scaled +    # Trend weight
            0.35 * median_scaled +   # Central tendency
            0.20 * fast_rate +       # Fast replies share
            0.10 * consistency       # Variability
        )
        
        # Determine verdict
        if score >= 75:
            verdict = "Strong interest 💕"
        elif score >= 55:
            verdict = "Moderate interest 💗"
        elif score >= 35:
            verdict = "Low interest 💙"
        else:
            verdict = "Very low interest 💔"
        
        breakdown = {
            'trend_score': round(slope_scaled * 35, 1),
            'speed_score': round(median_scaled * 35, 1),
            'fast_rate_score': round(fast_rate * 20, 1),
            'consistency_score': round(consistency * 10, 1)
        }
        
        return LoveScore(round(score), verdict, breakdown)
    
    def analyze_pair(self, target: str, counterpart: str) -> Dict:
        """
        Complete analysis for a participant pair
        Returns detailed metrics and love score
        """
        # Build reply series
        target_series, counterpart_series = self.build_reply_series(target, counterpart)
        
        # Compute regressions
        target_regression = self.compute_regression(target_series)
        counterpart_regression = self.compute_regression(counterpart_series)
        
        # Compute statistics
        target_stats = self.compute_stats(target_series)
        counterpart_stats = self.compute_stats(counterpart_series)
        
        # Calculate love score for target
        love_score = self.calculate_love_score(target_series, target_regression, target_stats)
        
        # Calculate love score for counterpart
        counterpart_love_score = self.calculate_love_score(
            counterpart_series, counterpart_regression, counterpart_stats
        )
        
        return {
            'target': {
                'name': target,
                'reply_count': target_stats.count,
                'median_reply_time': round(target_stats.median, 2),
                'mean_reply_time': round(target_stats.mean, 2),
                'std_dev': round(target_stats.std, 2),
                'fast_reply_rate': round(target_stats.fast_rate * 100, 1),
                'trend_slope': round(target_regression.slope, 4),
                'trend_r2': round(target_regression.r2, 4),
                'love_score': love_score.score,
                'verdict': love_score.verdict,
                'score_breakdown': love_score.breakdown
            },
            'counterpart': {
                'name': counterpart,
                'reply_count': counterpart_stats.count,
                'median_reply_time': round(counterpart_stats.median, 2),
                'mean_reply_time': round(counterpart_stats.mean, 2),
                'std_dev': round(counterpart_stats.std, 2),
                'fast_reply_rate': round(counterpart_stats.fast_rate * 100, 1),
                'trend_slope': round(counterpart_regression.slope, 4),
                'trend_r2': round(counterpart_regression.r2, 4),
                'love_score': counterpart_love_score.score,
                'verdict': counterpart_love_score.verdict,
                'score_breakdown': counterpart_love_score.breakdown
            },
            'comparison': {
                'faster_replier': target if target_stats.median < counterpart_stats.median else counterpart,
                'more_consistent': target if target_stats.std < counterpart_stats.std else counterpart,
                'improving_faster': target if target_regression.slope < counterpart_regression.slope else counterpart,
                'median_diff': abs(round(target_stats.median - counterpart_stats.median, 2))
            }
        }
    
    def get_love_scores(self) -> List[Dict]:
        """
        Calculate love scores for all participants
        Returns: List of dicts with sender, love_score, rank
        """
        from collections import Counter
        
        # Get all senders
        senders = [m.sender for m in self.messages if hasattr(m, 'sender') and m.sender]
        sender_counts = Counter(senders)
        unique_senders = list(sender_counts.keys())
        
        if len(unique_senders) < 2:
            return []
        
        # Calculate scores for each sender
        scores = []
        for sender in unique_senders:
            # Find their counterpart (the person they interact with most)
            counterparts = [s for s in unique_senders if s != sender]
            if not counterparts:
                continue
            
            # Analyze with primary counterpart
            try:
                analysis = self.analyze_pair(sender, counterparts[0])
                love_score = analysis['target']['love_score']
                
                scores.append({
                    'sender': sender,
                    'love_score': love_score,
                    'message_count': sender_counts[sender]
                })
            except:
                # If analysis fails, assign based on message count
                scores.append({
                    'sender': sender,
                    'love_score': min(100, sender_counts[sender] / 10),  # Simple fallback
                    'message_count': sender_counts[sender]
                })
        
        # Sort by love score descending
        scores.sort(key=lambda x: x['love_score'], reverse=True)
        
        # Add rank
        for idx, score in enumerate(scores, 1):
            score['rank'] = idx
        
        return scores
    
    def find_best_pairs(self, top_n: int = 5) -> List[Tuple[str, str, float]]:
        """
        Find participant pairs with highest combined love scores
        Returns: List of (person1, person2, combined_score)
        """
        # Get unique senders
        senders = list(set([m.sender for m in self.messages if hasattr(m, 'sender') and m.sender]))
        
        if len(senders) < 2:
            return []
        
        pairs = []
        for i in range(len(senders)):
            for j in range(i + 1, len(senders)):
                try:
                    analysis = self.analyze_pair(senders[i], senders[j])
                    combined_score = (
                        analysis['target']['love_score'] + 
                        analysis['counterpart']['love_score']
                    ) / 2
                    pairs.append((senders[i], senders[j], combined_score))
                except:
                    continue
        
        # Sort by combined score
        pairs.sort(key=lambda x: x[2], reverse=True)
        return pairs[:top_n]
