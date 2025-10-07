"""
Enhanced Defect Analytics Module for ReleaseGate
Provides comprehensive defect analysis, insights, and recommendations
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import numpy as np

def create_defect_analytics_dashboard(kpis, policy):
    """
    Create comprehensive defect analytics dashboard
    """
    st.markdown("## 🐛 Comprehensive Defect Analysis Dashboard")
    
    # Check if defect data is available
    defect_counts = kpis.get("defect_counts", {})
    total_defects = sum(defect_counts.values()) if defect_counts else 0
    
    if total_defects == 0:
        st.info("📝 **No defect data available** - Upload Excel file with defect_severity column or use manual entry to see detailed defect analysis.")
        return
    
    # === DEFECT OVERVIEW SECTION ===
    st.markdown("### 🎯 Defect Overview & Critical Metrics")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🚨 Total Defects",
            value=total_defects,
            delta=f"Critical: {defect_counts.get('Critical', 0)}",
            delta_color="inverse"
        )
    
    with col2:
        defect_density = total_defects / kpis.get('total_tests', 1) * 100
        st.metric(
            label="📊 Defect Density",
            value=f"{defect_density:.1f}%",
            delta="Per 100 tests",
            delta_color="off"
        )
    
    with col3:
        critical_blocked = defect_counts.get('Critical', 0) + defect_counts.get('Blocked', 0)
        st.metric(
            label="⛔ Critical+Blocked",
            value=critical_blocked,
            delta="High Risk",
            delta_color="inverse" if critical_blocked > 0 else "normal"
        )
    
    with col4:
        resolution_urgency = get_resolution_urgency_score(defect_counts)
        st.metric(
            label="⏰ Resolution Urgency",
            value=f"{resolution_urgency}/10",
            delta=get_urgency_label(resolution_urgency),
            delta_color="inverse" if resolution_urgency > 7 else "normal"
        )
    
    # === DEFECT DISTRIBUTION VISUALIZATIONS ===
    st.markdown("### 📈 Defect Distribution Analysis")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Enhanced Defect Severity Pie Chart
        create_defect_severity_pie_chart(defect_counts)
    
    with viz_col2:
        # Defect Lifecycle Status Chart
        create_defect_lifecycle_chart(kpis)
    
    # === DEFECT IMPACT ASSESSMENT ===
    st.markdown("### ⚖️ Defect Impact & Lifecycle Analysis")
    
    impact_col1, impact_col2 = st.columns(2)
    
    with impact_col1:
        # Defect Impact Assessment Chart
        create_defect_impact_chart(defect_counts, policy, kpis)
    
    with impact_col2:
        # Defect Lifecycle Ratios
        create_defect_ratios_chart(kpis)
    
    # === DEFECT RISK ASSESSMENT ===
    st.markdown("### ⚖️ Defect Risk Assessment Matrix")
    
    create_defect_risk_matrix(defect_counts, policy, kpis)
    
    # === DETAILED DEFECT BREAKDOWN ===
    st.markdown("### 🔍 Detailed Defect Breakdown")
    
    create_defect_breakdown_table(defect_counts, policy, kpis)
    
    # === DEFECT TRENDS AND PATTERNS ===
    st.markdown("### 📊 Defect Trends & Patterns")
    
    trend_col1, trend_col2 = st.columns(2)
    
    with trend_col1:
        create_defect_trend_analysis(defect_counts)
    
    with trend_col2:
        create_defect_age_analysis(kpis)
    
    # === TEAM AND ASSIGNMENT ANALYSIS ===
    if kpis.get('defect_assignee_distribution') or kpis.get('total_assignees'):
        st.markdown("### 👥 Team & Assignment Analysis")
        
        team_col1, team_col2 = st.columns(2)
        
        with team_col1:
            create_assignee_distribution_chart(kpis)
        
        with team_col2:
            create_team_workload_analysis(kpis)
    
    # === ACTIONABLE RECOMMENDATIONS ===
    st.markdown("### 💡 Defect Management Recommendations")
    
    create_defect_recommendations(defect_counts, policy, kpis)
    
    # === DEFECT RESOLUTION TIMELINE ===
    st.markdown("### ⏱️ Recommended Resolution Timeline")
    
    create_resolution_timeline(defect_counts)

def create_defect_severity_pie_chart(defect_counts):
    """Create enhanced defect severity distribution pie chart"""
    st.markdown("#### 🎯 Defect Severity Distribution")
    
    # Prepare data
    severities = list(defect_counts.keys())
    counts = list(defect_counts.values())
    total = sum(counts)
    
    if total == 0:
        st.info("No defects to display")
        return
    
    # Color mapping for severity levels
    color_map = {
        'Critical': '#dc2626',    # Red
        'Blocked': '#7c2d12',     # Dark red
        'Medium': '#f59e0b',      # Orange
        'Minor': '#10b981',       # Green
        'Low': '#6b7280'          # Gray
    }
    
    colors = [color_map.get(sev, '#6b7280') for sev in severities]
    
    # Create pie chart with enhanced styling
    fig = go.Figure(data=[
        go.Pie(
            labels=severities,
            values=counts,
            textinfo='label+percent+value',
            texttemplate='<b>%{label}</b><br>%{value} defects<br>%{percent}',
            hovertemplate='<b>%{label}</b><br>' +
                         'Count: %{value}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>',
            marker=dict(colors=colors, line=dict(color='#000000', width=2)),
            textfont=dict(size=12)
        )
    ])
    
    fig.update_layout(
        title={
            'text': "Defect Distribution by Severity",
            'x': 0.5,
            'font': {'size': 16, 'color': '#1f2937'}
        },
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_defect_lifecycle_chart(kpis):
    """Create defect lifecycle status distribution chart"""
    st.markdown("#### 🔄 Defect Lifecycle Status")
    
    # Check if lifecycle data is available
    if 'defect_status_counts' in kpis and kpis['defect_status_counts']:
        status_counts = kpis['defect_status_counts']
        
        # Create bar chart for defect status
        fig = go.Figure(data=[
            go.Bar(
                x=list(status_counts.keys()),
                y=list(status_counts.values()),
                marker_color=['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'],
                text=list(status_counts.values()),
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Defect Status Distribution",
            xaxis_title="Status",
            yaxis_title="Count",
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif kpis.get('open_defects', 0) > 0 or kpis.get('closed_defects', 0) > 0:
        # Manual entry data
        status_data = {
            'Open/In Progress': kpis.get('open_defects', 0),
            'Closed/Resolved': kpis.get('closed_defects', 0),
            'Rejected': kpis.get('rejected_defects', 0)
        }
        
        # Filter out zero values
        status_data = {k: v for k, v in status_data.items() if v > 0}
        
        if status_data:
            fig = go.Figure(data=[
                go.Bar(
                    x=list(status_data.keys()),
                    y=list(status_data.values()),
                    marker_color=['#ef4444', '#10b981', '#6b7280'],
                    text=list(status_data.values()),
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title="Defect Lifecycle Status",
                xaxis_title="Status",
                yaxis_title="Count",
                height=350,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No defect lifecycle data available")
    else:
        st.info("No defect lifecycle data available")

def create_defect_ratios_chart(kpis):
    """Create defect lifecycle ratios chart"""
    st.markdown("#### 📊 Defect Lifecycle Ratios")
    
    # Get ratios from KPIs
    open_rate = kpis.get('open_rate', 0) * 100
    closure_rate = kpis.get('closure_rate', 0) * 100
    rejection_rate = kpis.get('rejection_rate', 0) * 100
    
    if open_rate + closure_rate + rejection_rate > 0:
        # Create gauge charts for ratios
        fig = go.Figure()
        
        # Open Rate Gauge
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = open_rate,
            domain = {'row': 0, 'column': 0},
            title = {'text': "Open Rate (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "red"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 60], 'color': "yellow"},
                    {'range': [60, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig.update_layout(
            grid = {'rows': 1, 'columns': 1, 'pattern': "independent"},
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional metrics table
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Open Rate", f"{open_rate:.1f}%", 
                     delta="Higher is worse" if open_rate > 50 else "Acceptable")
        with col_b:
            st.metric("Closure Rate", f"{closure_rate:.1f}%", 
                     delta="Higher is better" if closure_rate > 50 else "Needs improvement")
        with col_c:
            st.metric("Rejection Rate", f"{rejection_rate:.1f}%", 
                     delta="High rejection rate" if rejection_rate > 20 else "Normal")
    else:
        st.info("No defect ratio data available")

def create_defect_impact_chart(defect_counts, policy, kpis=None):
    """Create defect business impact assessment chart using real uploaded data"""
    st.markdown("#### 💥 Business Impact Assessment")
    
    # Check if we have detailed defect information from uploaded data
    if kpis and 'defect_details' in kpis:
        defect_details = kpis['defect_details']
        
        # Extract business impacts from real data
        business_impacts = [d['business_impact'] for d in defect_details if d['business_impact'] and d['business_impact'].strip()]
        
        if business_impacts:
            # Show real business impacts from uploaded data
            st.markdown("**📋 Actual Business Impacts from Your Data:**")
            
            impact_summary = {}
            for impact in business_impacts:
                # Categorize impacts
                impact_lower = impact.lower()
                if any(word in impact_lower for word in ['revenue', 'sales', 'customer', 'payment', 'money']):
                    category = 'Revenue Impact'
                elif any(word in impact_lower for word in ['security', 'breach', 'vulnerability', 'data']):
                    category = 'Security Risk'
                elif any(word in impact_lower for word in ['system', 'crash', 'stability', 'performance']):
                    category = 'System Stability'
                elif any(word in impact_lower for word in ['user', 'experience', 'interface', 'usability']):
                    category = 'User Experience'
                else:
                    category = 'Operations'
                
                if category not in impact_summary:
                    impact_summary[category] = []
                impact_summary[category].append(impact)
            
            # Display categorized business impacts
            for category, impacts in impact_summary.items():
                with st.expander(f"🎯 {category} ({len(impacts)} defects)"):
                    for i, impact in enumerate(impacts, 1):
                        severity = next((d['severity'] for d in defect_details if d['business_impact'] == impact), 'Unknown')
                        status = next((d['status'] for d in defect_details if d['business_impact'] == impact), 'Unknown')
                        test_name = next((d['test_name'] for d in defect_details if d['business_impact'] == impact), 'Unknown')
                        
                        color = "🔴" if severity == "Critical" else "🟡" if severity == "Medium" else "🟢"
                        st.write(f"{color} **{severity}** | {status} | {test_name}")
                        st.write(f"   💼 {impact}")
                        st.write("")
            
            # Create impact severity chart
            severity_counts = {}
            for detail in defect_details:
                if detail['business_impact'] and detail['business_impact'].strip():
                    sev = detail['severity']
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            if severity_counts:
                categories = list(severity_counts.keys())
                counts = list(severity_counts.values())
                colors = {'Critical': '#dc2626', 'Medium': '#f59e0b', 'Minor': '#10b981', 'Blocked': '#7c2d12'}
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=categories,
                        y=counts,
                        marker=dict(color=[colors.get(cat, '#6b7280') for cat in categories]),
                        text=counts,
                        textposition='auto',
                    )
                ])
                
                fig.update_layout(
                    title="Business Impact by Defect Severity (From Your Data)",
                    xaxis_title="Defect Severity",
                    yaxis_title="Number of Defects with Business Impact",
                    height=350
                )
                
                st.plotly_chart(fig, use_container_width=True)
                return
    
    # Fallback to calculated scores if no real data available
    st.info("📊 Using calculated business impact scores (no detailed business impact data found in upload)")
    impact_scores = calculate_defect_impact_scores(defect_counts, policy)
    
    categories = list(impact_scores.keys())
    scores = list(impact_scores.values())
    
    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=categories,
            x=scores,
            orientation='h',
            marker=dict(
                color=scores,
                colorscale='Reds',
                colorbar=dict(title="Impact Score"),
                line=dict(color='rgba(0,0,0,0.5)', width=1)
            ),
            text=[f"{score:.1f}" for score in scores],
            textposition='inside',
            textfont=dict(color='white', size=12)
        )
    ])
    
    fig.update_layout(
        title="Business Impact by Category (Calculated)",
        xaxis_title="Impact Score (0-10)",
        yaxis_title="Impact Category",
        height=350,
        xaxis=dict(range=[0, 10])
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_defect_risk_matrix(defect_counts, policy, kpis):
    """Create defect risk assessment matrix"""
    
    # Risk matrix data
    risk_data = []
    
    for severity, count in defect_counts.items():
        if count > 0:
            probability = get_defect_probability(severity, count, kpis)
            impact = get_defect_impact_score(severity)
            risk_level = get_risk_level(probability, impact)
            
            risk_data.append({
                'Severity': severity,
                'Count': count,
                'Probability': probability,
                'Impact': impact,
                'Risk Level': risk_level,
                'Action Required': get_action_required(risk_level)
            })
    
    if risk_data:
        df = pd.DataFrame(risk_data)
        
        # Create risk matrix visualization
        fig = px.scatter(
            df, 
            x='Probability', 
            y='Impact',
            size='Count',
            color='Risk Level',
            hover_data=['Severity', 'Count', 'Action Required'],
            color_discrete_map={
                'Low': '#10b981',
                'Medium': '#f59e0b', 
                'High': '#ef4444',
                'Critical': '#dc2626'
            },
            title="Defect Risk Assessment Matrix"
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Probability (1-10)",
            yaxis_title="Impact (1-10)",
            xaxis=dict(range=[0, 11]),
            yaxis=dict(range=[0, 11])
        )
        
        # Add risk zone backgrounds
        fig.add_shape(
            type="rect", x0=0, y0=0, x1=5, y1=5,
            fillcolor="lightgreen", opacity=0.2, layer="below"
        )
        fig.add_shape(
            type="rect", x0=5, y0=5, x1=10, y1=10,
            fillcolor="lightcoral", opacity=0.2, layer="below"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk matrix table
        st.markdown("#### 📋 Risk Assessment Details")
        
        # Style the dataframe
        styled_df = df.style.apply(lambda x: [
            'background-color: #fee2e2' if v == 'Critical' 
            else 'background-color: #fef3c7' if v == 'High'
            else 'background-color: #f3f4f6' if v == 'Medium'
            else 'background-color: #f0fdf4' for v in x
        ], subset=['Risk Level'])
        
        st.dataframe(styled_df, use_container_width=True)

def create_defect_breakdown_table(defect_counts, policy, kpis=None):
    """Create detailed defect breakdown table with real uploaded data and policy compliance"""
    
    # Check if we have detailed defect information from uploaded data
    if kpis and 'defect_details' in kpis:
        defect_details = kpis['defect_details']
        
        if defect_details:
            st.markdown("#### 🔍 Detailed Defect Breakdown (From Your Upload)")
            
            # Create detailed table from real data
            table_data = []
            for detail in defect_details:
                # Policy compliance check
                severity = detail['severity']
                count_of_this_severity = defect_counts.get(severity, 0)
                compliance_status, compliance_message = check_policy_compliance(severity, count_of_this_severity, policy)
                
                table_data.append({
                    'Test': detail['test_name'] or 'N/A',
                    'Defect ID': detail['defect_id'] or 'N/A',
                    'Severity': detail['severity'],
                    'Type': detail['type'] or 'N/A',
                    'Status': detail['status'] or 'N/A',
                    'Detection Phase': detail['detection_phase'] or 'N/A',
                    'Root Cause': detail['root_cause'] or 'N/A',
                    'Impact Level': detail['impact_level'] or 'N/A',
                    'Likelihood': detail['likelihood'] or 'N/A',
                    'Business Impact': detail['business_impact'] or 'N/A',
                    'Policy Compliance': compliance_status
                })
            
            if table_data:
                df = pd.DataFrame(table_data)
                
                # Style the dataframe based on severity and compliance
                def style_row(row):
                    if row['Severity'] == 'Critical':
                        return ['background-color: #fee2e2'] * len(row)
                    elif row['Severity'] == 'Blocked':
                        return ['background-color: #fef3c7'] * len(row)
                    elif row['Severity'] == 'Medium':
                        return ['background-color: #fef3c7'] * len(row)
                    else:
                        return ['background-color: #f0fdf4'] * len(row)
                
                styled_df = df.style.apply(style_row, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
                # Summary of policy violations
                policy_violations = [item for item in table_data if item['Policy Compliance'] != '✅ Compliant']
                if policy_violations:
                    st.warning(f"⚠️ **Policy Violations Found:** {len(policy_violations)} defects violate quality policies")
                    for violation in policy_violations:
                        st.write(f"• {violation['Severity']} defect in {violation['Test']}: {violation['Policy Compliance']}")
                else:
                    st.success("✅ All defects comply with quality policies")
                
                return
    
    # Fallback to calculated breakdown if no real data available
    st.info("📊 Using calculated defect breakdown (no detailed defect data found in upload)")
    
    breakdown_data = []
    
    for severity, count in defect_counts.items():
        # Policy compliance check
        compliance_status, compliance_message = check_policy_compliance(severity, count, policy)
        
        # Recommended action
        action = get_recommended_action(severity, count, policy)
        
        # Priority level
        priority = get_defect_priority_level(severity)
        
        breakdown_data.append({
            'Severity': severity,
            'Count': count,
            'Policy Limit': get_policy_limit(severity, policy),
            'Compliance': compliance_status,
            'Priority Level': priority,
            'Recommended Action': action,
            'Estimated Resolution Time': get_estimated_resolution_time(severity, count)
        })
    
    df = pd.DataFrame(breakdown_data)
    
    # Create styled table
    def style_compliance(val):
        if val == "✅ Compliant":
            return 'background-color: #f0fdf4; color: #166534'
        elif val == "⚠️ Warning":
            return 'background-color: #fef3c7; color: #92400e'
        elif val == "❌ Non-Compliant":
            return 'background-color: #fee2e2; color: #dc2626'
        return ''
    
    styled_df = df.style.applymap(style_compliance, subset=['Compliance'])
    st.dataframe(styled_df, use_container_width=True)

def create_defect_trend_analysis(defect_counts):
    """Create defect trend analysis simulation"""
    st.markdown("#### 📈 Defect Trend Analysis")
    
    # Simulate historical data for trend analysis
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    
    trend_data = []
    for date in dates:
        # Simulate daily defect counts with some trend
        factor = (date - dates[0]).days / 30  # Increasing trend
        daily_counts = {}
        for severity, base_count in defect_counts.items():
            daily_count = max(0, int(base_count * (0.5 + factor * 0.5) * np.random.uniform(0.8, 1.2)))
            daily_counts[severity] = daily_count
        
        for severity, count in daily_counts.items():
            trend_data.append({
                'Date': date,
                'Severity': severity,
                'Count': count
            })
    
    trend_df = pd.DataFrame(trend_data)
    
    # Create line chart
    fig = px.line(
        trend_df, 
        x='Date', 
        y='Count', 
        color='Severity',
        color_discrete_map={
            'Critical': '#dc2626',
            'Blocked': '#7c2d12',
            'Medium': '#f59e0b',
            'Minor': '#10b981'
        },
        title="30-Day Defect Trend (Simulated)"
    )
    
    fig.update_layout(height=350, xaxis_title="Date", yaxis_title="Defect Count")
    st.plotly_chart(fig, use_container_width=True)

def create_defect_age_analysis(kpis):
    """Create defect age analysis"""
    st.markdown("#### ⏰ Defect Age Analysis")
    
    avg_age = kpis.get('avg_active_defect_age', 0)
    max_age = kpis.get('max_active_defect_age', 0)
    min_age = kpis.get('min_active_defect_age', 0)
    
    if avg_age > 0:
        # Create age distribution chart
        age_ranges = ['0-7 days', '8-14 days', '15-30 days', '31+ days']
        
        # Simulate age distribution based on average
        if avg_age <= 7:
            age_counts = [70, 20, 8, 2]
        elif avg_age <= 14:
            age_counts = [40, 40, 15, 5]
        elif avg_age <= 30:
            age_counts = [20, 30, 35, 15]
        else:
            age_counts = [10, 20, 35, 35]
        
        fig = go.Figure(data=[
            go.Bar(
                x=age_ranges,
                y=age_counts,
                marker_color=['#10b981', '#f59e0b', '#ef4444', '#dc2626'],
                text=age_counts,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Defect Age Distribution (%)",
            xaxis_title="Age Range",
            yaxis_title="Percentage",
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Age metrics
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Average Age", f"{avg_age:.1f} days")
        with col_b:
            st.metric("Oldest Defect", f"{max_age} days" if max_age > 0 else "N/A")
        with col_c:
            st.metric("Newest Defect", f"{min_age} days" if min_age > 0 else "N/A")
    else:
        st.info("No defect age data available")

def create_assignee_distribution_chart(kpis):
    """Create assignee distribution chart"""
    st.markdown("#### 👤 Defect Assignment Distribution")
    
    assignee_dist = kpis.get('defect_assignee_distribution', {})
    
    if assignee_dist:
        # Create horizontal bar chart for assignees
        assignees = list(assignee_dist.keys())
        counts = list(assignee_dist.values())
        
        fig = go.Figure(data=[
            go.Bar(
                y=assignees,
                x=counts,
                orientation='h',
                marker_color='#3b82f6',
                text=counts,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Defects by Assignee",
            xaxis_title="Number of Defects",
            yaxis_title="Team Member",
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        total_assignees = kpis.get('total_assignees', 0)
        if total_assignees > 0:
            st.metric("Team Members with Assigned Defects", total_assignees)
            st.info("Detailed assignee distribution not available from manual entry")
        else:
            st.info("No assignee data available")

def create_team_workload_analysis(kpis):
    """Create team workload analysis"""
    st.markdown("#### ⚖️ Team Workload Analysis")
    
    total_defects = kpis.get('total_defects', 0)
    total_assignees = kpis.get('total_assignees', 0)
    open_defects = kpis.get('open_defects', 0)
    
    if total_assignees > 0 and total_defects > 0:
        avg_defects_per_person = total_defects / total_assignees
        avg_open_per_person = open_defects / total_assignees if open_defects > 0 else 0
        
        # Workload indicators
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric(
                "Average Defects per Person", 
                f"{avg_defects_per_person:.1f}",
                delta="High workload" if avg_defects_per_person > 5 else "Balanced"
            )
        with col_b:
            st.metric(
                "Average Open Defects per Person", 
                f"{avg_open_per_person:.1f}",
                delta="Overloaded" if avg_open_per_person > 3 else "Manageable"
            )
        
        # Workload assessment
        if avg_defects_per_person > 8:
            st.error("🚨 **High Team Workload**: Consider redistributing defects or adding resources")
        elif avg_defects_per_person > 5:
            st.warning("⚠️ **Moderate Team Workload**: Monitor team capacity")
        else:
            st.success("✅ **Balanced Team Workload**: Team capacity appears appropriate")
            
        # Team efficiency indicators
        if total_defects > 0:
            team_efficiency = (kpis.get('closed_defects', 0) / total_defects) * 100
            st.markdown(f"**Team Resolution Efficiency**: {team_efficiency:.1f}%")
    else:
        st.info("Insufficient data for team workload analysis")

def create_defect_distribution_radar(defect_counts):
    """Create radar chart for defect distribution"""
    st.markdown("#### 🎯 Defect Profile Radar")
    
    severities = list(defect_counts.keys())
    counts = list(defect_counts.values())
    max_count = max(counts) if counts else 1
    
    # Normalize counts for radar chart
    normalized_counts = [count / max_count * 10 for count in counts]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=normalized_counts,
        theta=severities,
        fill='toself',
        name='Current Release',
        line=dict(color='#ef4444'),
        fillcolor='rgba(239, 68, 68, 0.3)'
    ))
    
    # Add benchmark line (ideal state - all low)
    benchmark = [2 if sev == 'Minor' else 1 if sev == 'Medium' else 0 for sev in severities]
    fig.add_trace(go.Scatterpolar(
        r=benchmark,
        theta=severities,
        fill='toself',
        name='Ideal Profile',
        line=dict(color='#10b981', dash='dash'),
        fillcolor='rgba(16, 185, 129, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=True,
        title="Defect Profile vs Ideal State",
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_defect_recommendations(defect_counts, policy, kpis):
    """Create actionable defect management recommendations"""
    
    recommendations = generate_defect_recommendations(defect_counts, policy, kpis)
    
    # Group recommendations by priority
    high_priority = [r for r in recommendations if r['priority'] == 'High']
    medium_priority = [r for r in recommendations if r['priority'] == 'Medium']
    low_priority = [r for r in recommendations if r['priority'] == 'Low']
    
    # Display high priority recommendations
    if high_priority:
        st.markdown("#### 🚨 **HIGH PRIORITY Actions**")
        for rec in high_priority:
            st.error(f"**{rec['title']}**: {rec['description']}")
    
    # Display medium priority recommendations
    if medium_priority:
        st.markdown("#### ⚠️ **MEDIUM PRIORITY Actions**")
        for rec in medium_priority:
            st.warning(f"**{rec['title']}**: {rec['description']}")
    
    # Display low priority recommendations
    if low_priority:
        st.markdown("#### ℹ️ **LOW PRIORITY Suggestions**")
        for rec in low_priority:
            st.info(f"**{rec['title']}**: {rec['description']}")

def create_resolution_timeline(defect_counts):
    """Create recommended resolution timeline"""
    
    timeline_data = []
    current_date = datetime.now()
    
    for severity, count in defect_counts.items():
        if count > 0:
            resolution_time = get_estimated_resolution_time(severity, count)
            due_date = current_date + timedelta(days=parse_resolution_time(resolution_time))
            
            timeline_data.append({
                'Severity': severity,
                'Count': count,
                'Start Date': current_date,
                'Due Date': due_date,
                'Days to Resolution': parse_resolution_time(resolution_time),
                'Status': get_timeline_status(severity)
            })
    
    if timeline_data:
        df = pd.DataFrame(timeline_data)
        # Format date columns for timeline chart
        df['Start Date'] = df['Start Date'].dt.strftime('%Y-%m-%d')
        df['Due Date'] = df['Due Date'].dt.strftime('%Y-%m-%d')
        
        # Create timeline chart
        fig = px.timeline(
            df,
            x_start='Start Date',
            x_end='Due Date',
            y='Severity',
            color='Status',
            title="Defect Resolution Timeline",
            color_discrete_map={
                'Critical': '#dc2626',
                'High': '#f59e0b',
                'Medium': '#3b82f6',
                'Normal': '#10b981'
            }
        )
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Timeline table
        st.dataframe(df, use_container_width=True)

# === HELPER FUNCTIONS ===

def get_resolution_urgency_score(defect_counts):
    """Calculate overall resolution urgency score (1-10)"""
    total_defects = sum(defect_counts.values())
    if total_defects == 0:
        return 0
    
    # Calculate weighted score with more balanced weights
    score = 0
    score += defect_counts.get('Critical', 0) * 3.0  # Reduced from 4
    score += defect_counts.get('Blocked', 0) * 2.5   # Reduced from 4
    score += defect_counts.get('Medium', 0) * 1.0    # Reduced from 2
    score += defect_counts.get('Minor', 0) * 0.2     # Reduced from 0.5
    
    # Normalize by total defects to avoid overwhelming scores
    normalized_score = (score / total_defects) * 2.5
    return min(10, max(1, round(normalized_score, 1)))

def get_urgency_label(score):
    """Get urgency label based on score"""
    if score >= 7:
        return "URGENT"
    elif score >= 5:
        return "High"
    elif score >= 3:
        return "Medium"
    else:
        return "Low"

def calculate_defect_impact_scores(defect_counts, policy):
    """Calculate business impact scores for different categories"""
    total_defects = sum(defect_counts.values())
    
    return {
        'Customer Experience': (defect_counts.get('Critical', 0) * 3 + defect_counts.get('Medium', 0)) / max(1, total_defects) * 10,
        'System Stability': (defect_counts.get('Critical', 0) * 4 + defect_counts.get('Blocked', 0) * 3) / max(1, total_defects) * 10,
        'Business Operations': (defect_counts.get('Critical', 0) * 2 + defect_counts.get('Medium', 0) * 1.5) / max(1, total_defects) * 10,
        'Development Velocity': (defect_counts.get('Blocked', 0) * 3 + defect_counts.get('Medium', 0)) / max(1, total_defects) * 10
    }

def get_defect_probability(severity, count, kpis):
    """Calculate probability score for defect occurrence"""
    base_prob = {'Critical': 9, 'Blocked': 8, 'Medium': 6, 'Minor': 4}.get(severity, 3)
    count_factor = min(3, count * 0.5)
    return min(10, base_prob + count_factor)

def get_defect_impact_score(severity):
    """Get impact score based on severity"""
    return {'Critical': 9, 'Blocked': 8, 'Medium': 6, 'Minor': 3}.get(severity, 2)

def get_risk_level(probability, impact):
    """Determine risk level based on probability and impact"""
    risk_score = probability * impact
    if risk_score >= 64:
        return 'Critical'
    elif risk_score >= 36:
        return 'High'
    elif risk_score >= 16:
        return 'Medium'
    else:
        return 'Low'

def get_action_required(risk_level):
    """Get required action based on risk level"""
    actions = {
        'Critical': 'Immediate action required',
        'High': 'Action required within 24h',
        'Medium': 'Action required within 1 week',
        'Low': 'Monitor and schedule fix'
    }
    return actions.get(risk_level, 'Monitor')

def check_policy_compliance(severity, count, policy):
    """Check if defect count complies with policy"""
    if severity in ['Critical', 'Blocked'] and policy.get('forbid_critical_or_blocked_defects', True):
        if count > 0:
            return "❌ Non-Compliant", f"Policy forbids {severity.lower()} defects"
    
    if severity == 'Medium' and count > policy.get('medium_defects_max', 2):
        return "❌ Non-Compliant", f"Exceeds limit of {policy.get('medium_defects_max', 2)}"
    
    if severity == 'Minor' and count > policy.get('minor_defects_note_threshold', 5):
        return "⚠️ Warning", f"Above threshold of {policy.get('minor_defects_note_threshold', 5)}"
    
    return "✅ Compliant", "Within policy limits"

def get_policy_limit(severity, policy):
    """Get policy limit for severity"""
    if severity in ['Critical', 'Blocked']:
        return "0 (Forbidden)" if policy.get('forbid_critical_or_blocked_defects', True) else "No limit"
    elif severity == 'Medium':
        return str(policy.get('medium_defects_max', 2))
    elif severity == 'Minor':
        return f"{policy.get('minor_defects_note_threshold', 5)} (warning)"
    return "No limit"

def get_recommended_action(severity, count, policy):
    """Get recommended action for defect severity"""
    if severity == 'Critical':
        return "Block release, fix immediately"
    elif severity == 'Blocked':
        return "Unblock tests, fix underlying issues"
    elif severity == 'Medium' and count > policy.get('medium_defects_max', 2):
        return "Fix before release or get approval"
    elif severity == 'Minor' and count > policy.get('minor_defects_note_threshold', 5):
        return "Review and prioritize fixes"
    else:
        return "Monitor and schedule fix in next sprint"

def get_defect_priority_level(severity):
    """Get priority level for defect"""
    priorities = {
        'Critical': 'P0 - Critical',
        'Blocked': 'P0 - Critical', 
        'Medium': 'P1 - High',
        'Minor': 'P2 - Medium'
    }
    return priorities.get(severity, 'P3 - Low')

def get_estimated_resolution_time(severity, count):
    """Get estimated resolution time"""
    base_times = {
        'Critical': 1,  # days
        'Blocked': 2,
        'Medium': 5,
        'Minor': 10
    }
    base_time = base_times.get(severity, 7)
    total_time = base_time + (count - 1) * (base_time * 0.5)
    
    if total_time <= 1:
        return "1 day"
    elif total_time <= 7:
        return f"{int(total_time)} days"
    else:
        weeks = total_time / 7
        return f"{weeks:.1f} weeks"

def parse_resolution_time(time_str):
    """Parse resolution time string to days"""
    if "day" in time_str:
        return int(time_str.split()[0])
    elif "week" in time_str:
        return int(float(time_str.split()[0]) * 7)
    return 7

def get_timeline_status(severity):
    """Get timeline status color"""
    return {
        'Critical': 'Critical',
        'Blocked': 'Critical',
        'Medium': 'High', 
        'Minor': 'Medium'
    }.get(severity, 'Normal')

def generate_defect_recommendations(defect_counts, policy, kpis):
    """Generate actionable recommendations based on defect analysis"""
    recommendations = []
    
    # Critical defects
    if defect_counts.get('Critical', 0) > 0:
        recommendations.append({
            'priority': 'High',
            'title': 'Critical Defects Detected',
            'description': f"There are {defect_counts['Critical']} critical defects that must be fixed before release. These directly impact system functionality and user experience."
        })
    
    # Blocked defects
    if defect_counts.get('Blocked', 0) > 0:
        recommendations.append({
            'priority': 'High',
            'title': 'Blocked Tests Need Resolution',
            'description': f"{defect_counts['Blocked']} tests are blocked. Investigate and resolve blocking issues to complete test coverage."
        })
    
    # Medium defects over policy
    medium_count = defect_counts.get('Medium', 0)
    medium_limit = policy.get('medium_defects_max', 2)
    if medium_count > medium_limit:
        recommendations.append({
            'priority': 'Medium',
            'title': 'Medium Defects Exceed Policy',
            'description': f"Found {medium_count} medium defects (limit: {medium_limit}). Consider fixing critical ones or getting stakeholder approval."
        })
    
    # Minor defects warning
    minor_count = defect_counts.get('Minor', 0)
    minor_threshold = policy.get('minor_defects_note_threshold', 5)
    if minor_count > minor_threshold:
        recommendations.append({
            'priority': 'Low',
            'title': 'High Number of Minor Defects',
            'description': f"Found {minor_count} minor defects (threshold: {minor_threshold}). Consider addressing in next sprint to prevent accumulation."
        })
    
    # Overall defect density
    total_defects = sum(defect_counts.values())
    total_tests = kpis.get('total_tests', 1)
    defect_density = total_defects / total_tests * 100
    
    if defect_density > 10:
        recommendations.append({
            'priority': 'Medium',
            'title': 'High Defect Density',
            'description': f"Defect density is {defect_density:.1f}% (>10%). Consider improving test practices and code quality measures."
        })
    
    return recommendations