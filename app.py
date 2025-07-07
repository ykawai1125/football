# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set page config
st.set_page_config(
    page_title="Premier League Analytics",
    page_icon="⚽",
    layout="wide"
)

# Load data function
@st.cache_data
def load_data():
    data_dir = "data"
    return {
        'fixtures': pd.read_csv(os.path.join(data_dir, 'fixtures.csv')),
        'player_possession': pd.read_csv(os.path.join(data_dir, 'player_possession_stats.csv')),
        'player_salaries': pd.read_csv(os.path.join(data_dir, 'player_salaries.csv')),
        'player_stats': pd.read_csv(os.path.join(data_dir, 'player_stats.csv')),
        'standings': pd.read_csv(os.path.join(data_dir, 'standings.csv')),
        'team_possession': pd.read_csv(os.path.join(data_dir, 'team_possession_stats.csv')),
        'team_salary': pd.read_csv(os.path.join(data_dir, 'team_salary.csv')),
        'team_stats': pd.read_csv(os.path.join(data_dir, 'team_stats.csv'))
    }

def main():
    st.sidebar.title("⚽ Premier League Analytics")
    data = load_data()
    
    # Navigation
    page = st.sidebar.radio("Go to", [
        "🏆 League Standings",
        "📊 Team Analysis",
        "👤 Player Analysis",
        "📅 Match Fixtures"
    ])
    
    if page == "🏆 League Standings":
        show_standings(data)
    elif page == "📊 Team Analysis":
        show_team_analysis(data)
    elif page == "👤 Player Analysis":
        show_player_analysis(data)
    elif page == "📅 Match Fixtures":
        show_fixtures(data)

def show_standings(data):
    st.title("🏆 Premier League Standings")
    
    # Current table
    st.subheader("Current League Table")
    standings = data['standings'].sort_values('rank')
    st.dataframe(standings, use_container_width=True)
    
    # Points visualization
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(standings, x='team', y='points', 
                    title='Points by Team', color='points')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(standings, names='team', values='points',
                    title='Points Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Last 5 form analysis
    st.subheader("Recent Form Analysis")
    selected_teams = st.multiselect("Select teams to compare", 
                                  standings['team'].unique())
    if selected_teams:
        form_data = standings[standings['team'].isin(selected_teams)]
        fig = px.bar(form_data, x='team', y='points', color='last5',
                    title='Points vs Recent Form')
        st.plotly_chart(fig, use_container_width=True)

def show_team_analysis(data):
    st.title("📊 Team Performance Analysis")
    
    # Team selector
    selected_team = st.selectbox("Select Team", 
                               data['team_stats']['team'].unique())
    
    # Team stats
    team_data = data['team_stats'][data['team_stats']['team'] == selected_team].iloc[0]
    
    # Key metrics
    st.subheader(f"{selected_team} Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Goals Scored", team_data['goals'])
        st.metric("Expected Goals (xG)", round(team_data['expected_goals'], 2))
    
    with col2:
        st.metric("Possession %", f"{team_data['possession']}%")
        st.metric("Progressive Passes", team_data['progressive_passes'])
    
    with col3:
        st.metric("Yellow Cards", team_data['yellows'])
        st.metric("Red Cards", team_data['reds'])
    
    # Salary analysis
    st.subheader("Team Salary Distribution")
    salary_data = data['team_salary'][data['team_salary']['team'] == selected_team]
    if not salary_data.empty:
        fig = px.pie(salary_data, values='weekly', names='players',
                    title='Weekly Salary Breakdown')
        st.plotly_chart(fig, use_container_width=True)
    
    # Possession stats
    st.subheader("Possession Analysis")
    possession_data = data['team_possession'][data['team_possession']['team'] == selected_team].iloc[0]
    
    fig = px.bar(x=['Defensive', 'Middle', 'Attacking'],
                y=[possession_data['deffensive_touches'], 
                   possession_data['middle_touches'], 
                   possession_data['attacking_touches']],
                title='Touches by Zone')
    st.plotly_chart(fig, use_container_width=True)

def show_player_analysis(data):
    st.title("👤 Player Performance Analysis")
    
    # Player selector
    selected_player = st.selectbox("Select Player", 
                                 data['player_stats']['name'].unique())
    
    try:
        # Get player data with correct column names
        player_stats = data['player_stats'][data['player_stats']['name'] == selected_player].iloc[0]
        player_possession = data['player_possession'][data['player_possession']['player'] == selected_player].iloc[0]
        player_salary = data['player_salaries'][data['player_salaries']['Player'] == selected_player].iloc[0]
        
        # Display player info
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Player Information")
            st.write(f"**Team:** {player_stats['team']}")
            st.write(f"**Position:** {player_stats['position']}")
            st.write(f"**Age:** {player_stats['age']}")
            st.write(f"**Weekly Salary:** £{player_salary['Weekly']:,}")
            
            st.subheader("Performance Stats")
            st.write(f"**Goals:** {player_stats['goals']}")
            st.write(f"**Assists:** {player_stats['assists']}")
            if 'expected_goals' in player_stats:
                st.write(f"**Expected Goals (xG):** {round(player_stats['expected_goals'], 2)}")
        
        with col2:
            st.subheader("Possession Stats")
            st.write(f"**Successful Take-ons:** {player_possession['successful_take_ons']}")
            if 'progressive_carries' in player_stats:
                st.write(f"**Progressive Carries:** {player_stats['progressive_carries']}")
            if 'progressive_passes' in player_stats:
                st.write(f"**Progressive Passes:** {player_stats['progressive_passes']}")
            
            st.subheader("Salary Information")
            st.write(f"**Annual Salary:** £{player_salary['Annual']:,}")
            if 'minutes' in player_stats:
                st.write(f"**Minutes Played:** {player_stats['minutes']}")
    
    except Exception as e:
        st.error(f"Error loading player data: {str(e)}")
        st.write("Please check if:")
        st.write("- The player exists in all data files")
        st.write("- Column names match between code and CSV files")
def show_fixtures(data):
    st.title("📅 Match Fixtures and Results")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        selected_team = st.selectbox("Filter by Team", 
                                   ['All Teams'] + list(data['fixtures']['Home'].unique()))
    with col2:
        date_range = st.date_input("Filter by Date Range", 
                                  [pd.to_datetime(data['fixtures']['Date'].min()),
                                   pd.to_datetime(data['fixtures']['Date'].max())])
    
    # Apply filters
    fixtures = data['fixtures'].copy()
    fixtures['Date'] = pd.to_datetime(fixtures['Date'])
    
    if selected_team != 'All Teams':
        fixtures = fixtures[(fixtures['Home'] == selected_team) | 
                          (fixtures['Away'] == selected_team)]
    
    fixtures = fixtures[(fixtures['Date'] >= pd.to_datetime(date_range[0])) & 
                       (fixtures['Date'] <= pd.to_datetime(date_range[1]))]
    
    # Display fixtures
    st.dataframe(fixtures.sort_values('Date'), use_container_width=True)
    
    # Results analysis
    st.subheader("Results Analysis")
    if not fixtures.empty:
        home_wins = len(fixtures[fixtures['HomeScore'] > fixtures['AwayScore']])
        away_wins = len(fixtures[fixtures['AwayScore'] > fixtures['HomeScore']])
        draws = len(fixtures[fixtures['HomeScore'] == fixtures['AwayScore']])
        
        fig = px.pie(values=[home_wins, away_wins, draws], 
                     names=['Home Wins', 'Away Wins', 'Draws'],
                     title='Match Results Distribution')
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()