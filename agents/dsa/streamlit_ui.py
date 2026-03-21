import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from agents.dsa import (
    get_all_topics,
    progress_tracker,
    get_topic_problems,
    get_topic_info,
    generate_daily_schedule,
    get_easy_problems,
    get_medium_problems,
    generate_problem_explanation,
    TIME_PLAN_CONFIGS,
)

def render_dsa_tutor():
    """Main DSA Tutor Interface"""
    
    st.header("🎯 DSA Learning Tutor")
    st.markdown("---")
    
    # Initialize session state
    if 'selected_tab' not in st.session_state:
        st.session_state.selected_tab = 0
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs([
        "📋 Roadmap & Daily Plan", 
        "🎯 Daily Challenge"
    ])
    
    # TAB 1: ROADMAP SELECTOR
    with tab1:
        render_roadmap_selector()
    
    # TAB 2: DAILY CHALLENGE
    with tab2:
        render_daily_challenge()


def render_roadmap_selector():
    """Select roadmap duration and show weekly topic breakdown"""
    
    st.subheader("Select Your Learning Plan")
    st.write("Choose a plan: 1 Easy + 1 Medium problem per day")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📅 3-Month Plan (90 Days)", use_container_width=True, key="3month"):
            st.session_state.selected_plan = "3_months"
    
    with col2:
        if st.button("📅 6-Month Plan (180 Days)", use_container_width=True, key="6month"):
            st.session_state.selected_plan = "6_months"
    
    st.markdown("---")
    
    # Show plan details
    st.subheader("Plan Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **3-Month Plan**
        - Duration: 90 days
        - Daily: 1 Easy + 1 Medium
        - Total: 180 problems
        - Pace: Intensive (Best for focused prep)
        """)
    
    with col2:
        st.info("""
        **6-Month Plan**
        - Duration: 180 days
        - Daily: 1 Easy + 1 Medium
        - Total: 360 problems (cycling)
        - Pace: Moderate (Good for learning & retention)
        """)
    
    st.markdown("---")
    
    # Show weekly topic breakdown if plan is selected
    if 'selected_plan' in st.session_state and st.session_state.selected_plan:
        plan = st.session_state.selected_plan
        months = int(plan.split('_')[0])
        
        st.subheader(f"📅 Weekly Topic Breakdown - {months}-Month Plan")
        st.success(f"✅ {months}-Month Plan Selected!")
        
        # Generate daily schedule
        daily_schedule = generate_daily_schedule(months)
        
        if daily_schedule:
            # Group by weeks
            weeks_topics = {}
            
            for day_assignment in daily_schedule:
                day = day_assignment['day']
                week = (day - 1) // 7 + 1  # Calculate week number (1-indexed)
                easy_topic = day_assignment.get('easy_topic', 'N/A')
                medium_topic = day_assignment.get('medium_topic', 'N/A')
                
                if week not in weeks_topics:
                    weeks_topics[week] = set()
                
                if easy_topic != 'N/A':
                    weeks_topics[week].add(easy_topic)
                if medium_topic != 'N/A':
                    weeks_topics[week].add(medium_topic)
            
            # Display weekly breakdown
            for week_num in sorted(weeks_topics.keys()):
                topics_in_week = sorted(list(weeks_topics[week_num]))
                
                with st.expander(f"📚 Week {week_num} - Topics: {', '.join(topics_in_week)}", expanded=False):
                    # Calculate day range for this week
                    start_day = (week_num - 1) * 7 + 1
                    end_day = min(week_num * 7, len(daily_schedule))
                    
                    st.write(f"**Days {start_day}-{end_day}**")
                    st.write(f"**Topics to focus on:** {', '.join(topics_in_week)}")
                    
                    # Show daily breakdown for this week
                    week_data = []
                    for day in range(start_day, end_day + 1):
                        if day <= len(daily_schedule):
                            day_assignment = daily_schedule[day - 1]
                            week_data.append({
                                "Day": f"Day {day}",
                                "Easy Topic": day_assignment.get('easy_topic', 'N/A'),
                                "Medium Topic": day_assignment.get('medium_topic', 'N/A')
                            })
                    
                    if week_data:
                        week_df = pd.DataFrame(week_data)
                        st.dataframe(week_df, use_container_width=True, hide_index=True)



def render_daily_challenge():
    """Daily learning challenge with direct problem links"""
    
    # Check if plan is selected
    if 'selected_plan' not in st.session_state or not st.session_state.selected_plan:
        st.warning("⚠️ Please select a plan first in the **📋 Roadmap & Daily Plan** tab")
        st.info("Click on either **3-Month Plan** or **6-Month Plan** to get started!")
        return
    
    plan = st.session_state.selected_plan
    st.subheader(f"🎯 Daily Challenge - {plan.replace('_', ' ').title()}")
    
    # Generate daily schedule
    months = int(plan.split('_')[0])
    daily_schedule = generate_daily_schedule(months)
    
    if not daily_schedule:
        st.error("Failed to generate daily schedule. Please try again.")
        return
    
    # Initialize current_day in session state if not present
    total_days = len(daily_schedule)
    if 'current_day' not in st.session_state:
        st.session_state.current_day = 1
    
    # Show summary
    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Total Days", total_days)
    col2.metric("📊 Daily Requirement", "1 Easy + 1 Medium")
    col3.metric("🎯 Total Problems", f"{total_days * 2}")
    
    st.markdown("---")
    
    # Day selector
    selected_day = st.slider("📍 Select a Day:", 1, total_days, st.session_state.current_day, key="day_slider")
    
    # Get the selected day's assignment
    day_assignment = daily_schedule[selected_day - 1]
    
    # Update session state with current day selection
    st.session_state.current_day = selected_day
    
    # Calculate progress
    overall_progress = progress_tracker.get_all_progress()
    progress_pct = overall_progress['overall_completion']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Today's Day", f"{selected_day}/{total_days}")
    col2.metric("⏳ Days Remaining", total_days - selected_day + 1)
    col3.metric("✅ Overall Progress", f"{progress_pct}%")
    
    st.progress(progress_pct / 100)
    st.markdown("---")
    
    # Display day header
    st.subheader(f"📅 Day {selected_day} of {total_days}")
    
    col1, col2 = st.columns(2)
    
    # Easy Problem
    with col1:
        st.markdown("### 🟢 Easy Problem")
        easy_problem = day_assignment['easy_problem']
        if easy_problem:
            easy_topic = day_assignment['easy_topic']
            easy_problem_id = easy_problem['id']
            
            # Get current completion status from progress tracker
            topic_progress = progress_tracker.get_topic_progress(easy_topic)
            is_easy_completed = topic_progress['problems'][easy_problem_id]['completed']
            
            st.markdown(f"**LeetCode #{easy_problem['id']}: {easy_problem['name']}**")
            st.markdown(f"⏱️ Est. Time: **{easy_problem['time_estimate_mins']}** mins")
            
            # Checkbox for completion
            easy_key = f"easy_complete_{selected_day}"
            easy_completed = st.checkbox(
                "✅ Mark as Completed",
                value=is_easy_completed,
                key=easy_key
            )
            
            # Save to progress tracker if status changed
            if easy_completed != is_easy_completed:
                if easy_completed:
                    progress_tracker.mark_problem_completed(easy_topic, easy_problem_id)
                else:
                    progress_tracker.mark_problem_incomplete(easy_topic, easy_problem_id)
            
            # LeetCode Link Button
            st.markdown(f"### [🔗 Go to LeetCode Problem](https://leetcode.com/problems/{easy_problem['leetcode_link'].split('/')[-2]}/)") 
            
            st.info(f"**Topic:** {easy_topic}")
        st.markdown("### 🟡 Medium Problem")
        medium_problem = day_assignment['medium_problem']
        if medium_problem:
            medium_topic = day_assignment['medium_topic']
            medium_problem_id = medium_problem['id']
            
            # Get current completion status from progress tracker
            topic_progress = progress_tracker.get_topic_progress(medium_topic)
            is_medium_completed = topic_progress['problems'][medium_problem_id]['completed']
            
            st.markdown(f"**LeetCode #{medium_problem['id']}: {medium_problem['name']}**")
            st.markdown(f"⏱️ Est. Time: **{medium_problem['time_estimate_mins']}** mins")
            
            # Checkbox for completion
            medium_key = f"medium_complete_{selected_day}"
            medium_completed = st.checkbox(
                "✅ Mark as Completed",
                value=is_medium_completed,
                key=medium_key
            )
            
            # Save to progress tracker if status changed
            if medium_completed != is_medium_completed:
                if medium_completed:
                    progress_tracker.mark_problem_completed(medium_topic, medium_problem_id)
                else:
                    progress_tracker.mark_problem_incomplete(medium_topic, medium_problem_id)
            
            # LeetCode Link Button
            st.markdown(f"### [🔗 Go to LeetCode Problem](https://leetcode.com/problems/{medium_problem['leetcode_link'].split('/')[-2]}/)") 
            
            st.info(f"**Topic:** {medium_topic}")
    # Navigation buttons
    st.subheader("📌 Quick Navigation")
    
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    # Previous day button
    with nav_col1:
        if selected_day > 1:
            if st.button("⬅️ Previous Day", use_container_width=True):
                st.session_state.current_day = selected_day - 1
        else:
            st.button("⬅️ Previous Day", use_container_width=True, disabled=True)
    
    # Show current week overview
    with nav_col2:
        week_start = ((selected_day - 1) // 7) * 7 + 1
        week_end = min(week_start + 6, total_days)
        st.write(f"📅 **Week {(selected_day - 1) // 7 + 1}** (Days {week_start}-{week_end})")
    
    # Next day button
    with nav_col3:
        if selected_day < total_days:
            if st.button("Next Day ➡️", use_container_width=True):
                st.session_state.current_day = selected_day + 1
        else:
            st.button("Next Day ➡️", use_container_width=True, disabled=True)
    
    st.markdown("---")
    
    # Show circular progress tracker
    st.subheader("📊 Your Progress Overview")
    
    # Get progress by difficulty
    difficulty_progress = progress_tracker.get_progress_by_difficulty()
    
    easy = difficulty_progress['easy']
    medium = difficulty_progress['medium']
    hard = difficulty_progress['hard']
    
    overall_progress = progress_tracker.get_all_progress()
    total_completed = overall_progress['completed_problems']
    total_problems = overall_progress['total_problems']
    
    # Create circular progress visualization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create donut chart
        labels = ['Completed', 'Remaining']
        values = [total_completed, total_problems - total_completed]
        colors = ['#4CAF50', '#E8F5E9']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.7,
            marker=dict(colors=colors),
            textposition='inside',
            textinfo='label+percent',
            hoverinfo='label+value'
        )])
        
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Show statistics
        st.metric("Total Solved", f"{total_completed}/{total_problems}")
        st.metric("Completion %", f"{overall_progress['overall_completion']}%")
    
    st.markdown("---")
    
    # Difficulty breakdown
    st.subheader("💪 By Difficulty Level")
    
    diff_col1, diff_col2, diff_col3 = st.columns(3)
    
    with diff_col1:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: #E8F5E9; border-radius: 10px;'>
            <h3 style='color: #4CAF50; margin: 0;'>🟢 Easy</h3>
            <p style='font-size: 24px; margin: 10px 0; color: #2E7D32;'>{easy['completed']}/{easy['total']}</p>
            <p style='color: #558B2F; margin: 0;'>{easy['percentage']}% Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with diff_col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: #FFF3E0; border-radius: 10px;'>
            <h3 style='color: #F57C00; margin: 0;'>🟡 Medium</h3>
            <p style='font-size: 24px; margin: 10px 0; color: #E65100;'>{medium['completed']}/{medium['total']}</p>
            <p style='color: #BF360C; margin: 0;'>{medium['percentage']}% Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with diff_col3:
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background: #FFEBEE; border-radius: 10px;'>
            <h3 style='color: #D32F2F; margin: 0;'>🔴 Hard</h3>
            <p style='font-size: 24px; margin: 10px 0; color: #B71C1C;'>{hard['completed']}/{hard['total']}</p>
            <p style='color: #880E4F; margin: 0;'>{hard['percentage']}% Completed</p>
        </div>
        """, unsafe_allow_html=True)

