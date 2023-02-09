import streamlit as st

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_plotly_events import plotly_events

from scipy.interpolate import make_interp_spline

import datetime as dt

def title():
    # Heading
    st.markdown("# Bedroom Analysis \n ---")

def cleaning(df: pd.DataFrame):
    """
    Cleaning and processing raw data
    """
    df.columns = ["index", "datetime", "mG", "V/m", "mW/m2", "microW/m2", "source"]
    df["source"] = pd.Categorical(df["source"])
    return df

class Analysis():
    def __init__(self, col: str):
        self.df = pd.read_excel("Amruth_Bedroom_Analysis.xlsx", usecols="A:F,H")
        self.df = cleaning(self.df)

        # Columns names
        self.col = col

        # Set params
        sns.set_style("whitegrid")
        sns.set_palette("winter")

        self.sleep = dt.datetime(2023, 1, 6, 23)
        self.awake = dt.datetime(2023, 1, 7, 5, 40)

    def plot_all(self):
        """
        Function call and plot all graphs
        """
        # Initial calculation
        self.calculate()

        # Raw graph
        self.raw_analysis()
        if self.col == "microW/m2":
            st.markdown(
                "The graph above is a bird's eye view of EMF Radiation from a bedroom takenover 24 hours."
                " Note that the scale goes upto 700k! Relevant human activity has been highlighted. The "
                "graph below breaks down what happens during the night.\n"
                )
        self.sleep_graph()

        # Frequency
        st.markdown("### Frequency Plots\n")
        if self.col == "microW/m2":
            st.markdown(
                "The plots below are frequency plots of EMF readings split from different human activity. "
                "As seen, the median value is close to 2.5k while the mean lies around 4k during active hours. "
                "Important here to understand that the radiation over the safety threshold persists over 12 hours a day! "
                "While data during sleep is a mere 6.5 hours."
            )
        self.frequency_graphs()

        # Outliers
        st.markdown("### Outliers \n")
        if self.col == "microW/m2":
            st.markdown(
                "The plots below focus and highlight the outliers and suspected activity. Seen below with an overview of outlier points "
                "is a 2 minute period of exposure to extreme levels of radiation. This far surpases what is the daily average."
            )
        self.raw_outliers()
        self.specific8pm()

        # Inliers
        st.markdown("### Inliers \n")
        st.markdown(
            "Focusing on the points that exist within the normal range of the data, the plot seen below shows the density of points "
            "that exist during the day."
        )
        self.raw_inlier()
        self.moving_average()

    def calculate(self):
        # Raw numbers
        self.avg = self.df[self.col].mean()
        self.std = self.df[self.col].std()

        self.normal_df = self.df[self.df[self.col] < (self.avg + (2 * self.std))].copy()
        self.outliers_df = self.df[self.df[self.col] > (self.avg + (2 * self.std))]
        self.df["outliers"] = self.df[self.col] > (self.avg + (2 * self.std))

        self.sleep_df = self.normal_df[(self.normal_df["datetime"] > self.sleep) & (self.normal_df["datetime"] < self.awake)]
        self.awake_df = self.normal_df[(self.normal_df["datetime"] < self.sleep) | (self.normal_df["datetime"] > self.awake)]

        # Moving averages
        self.normal_df["MA60"] = self.normal_df[self.col].rolling(60).mean()
        self.normal_df["MA180"] = self.normal_df[self.col].rolling(180).mean()
        self.normal_df["MA300"] = self.normal_df[self.col].rolling(300).mean()

        # Specific columns and safe levels
        if self.col == "microW/m2":
            self.symbol = "μW/m\u00b2"
            self.ytitle = "EMF Radiation"
            self.safe_level = 1000
        elif self.col == "mG":
            self.symbol = "mG"
            self.ytitle = "MF"
            self.safe_level = 0   
        elif self.col == "V/m":
            self.symbol = "V/m"
            self.ytitle = "EF"
            self.safe_level = 0

    def raw_analysis(self):
        """
        Raw bare-bones analysis of given
        """
        fig = go.Figure()

        fig.add_scatter(
            x = self.df["datetime"],
            y = self.df[self.col],
            opacity=0.8,
        )
        fig.add_vline(
            x = self.sleep.timestamp() * 1000,
            line_dash = "dot",
            line_color = "black",
            annotation_text = "11:00 pm",
            annotation_position = "top right",
            annotation_font_color = "white"
        )
        fig.add_vline(
            x = self.awake.timestamp() * 1000,
            line_dash = "dot",
            line_color = "black",
            annotation_text = "5:30 am",
            annotation_position = "top left",
            annotation_font_color = "white"
        )
        fig.add_vrect(
            x0=self.sleep.timestamp() * 1000,
            x1=self.awake.timestamp() * 1000,
            fillcolor = "black",
            opacity=0.33
        )
        fig.update_layout(
            title= self.ytitle + " over a day",
            xaxis_title = "Time",
            yaxis_title = self.ytitle + "(" + self.symbol + ")"
        )

        st.plotly_chart(fig)

    def sleep_graph(self):
        """
        Plot sleeping hours graph
        """
        fig = go.Figure()

        fig = px.scatter(
            self.sleep_df,
            x="datetime",
            y=self.col,
            opacity=0.5,
            trendline="rolling",
            trendline_color_override="blue",
            trendline_options=dict(window=600)
            )

        fig.update_layout(
            title=self.ytitle + " during night hours (11:00 pm - 5:30 am)",
            xaxis_title="Time",
            yaxis_title=self.ytitle + "(" + self.symbol + ")"
        )

        fig.update_traces(
            marker=dict(color="darkgrey")
        )

        st.plotly_chart(fig)

    def frequency_graphs(self):
        """
        Calculate frequency graphs
        """
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=(self.ytitle + " Count during active hours (15 hrs)", self.ytitle + " Count during sleep hours (6.5 hrs)")
            )

        fig.add_trace(
            go.Histogram(
                # Checking above safe limit
                x = self.awake_df[self.col],
                nbinsx=200,
                opacity=0.6,
                marker_color="blue"
            ),
            row=1,
            col=1
        )

        # Safe level only applies to EMF
        if self.safe_level != 0:
            fig.add_vline(
                x = self.safe_level,
                line_dash = "dot",
                line_color = "red",
                opacity = 0.4,
                annotation_text = "Safe level",
                annotation_position = "top right",
                annotation_font_color = "red",
                annotation_opacity= 0.6
            )

        fig.add_trace(
            go.Histogram(
                x = self.sleep_df[self.col],
                nbinsx=200,
                marker_color="darkgrey",
            ),
            row=1,
            col=2
        )

        # Update meta-data
        fig.update_layout(
            showlegend=False,
            title_text=self.ytitle + " count throughout the day",
            )
        fig.update_xaxes(title_text=self.ytitle + "(" + self.symbol + ")", row=1, col=1)
        fig.update_xaxes(title_text=self.ytitle + "(" + self.symbol + ")", row=1, col=2)
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=2)

        st.plotly_chart(fig)

    def raw_outliers(self):
        """
        Function to output raw graph with colored outliers
        """
        fig = px.scatter(
            data_frame=self.df,
            x = "datetime",
            y = self.col,
            opacity=0.4,
            color="outliers",
            color_discrete_map = {
                True : "red",
                False : "blue"
            }
        )
        
        fig.update_layout(
            title=self.ytitle + " with outliers",
            xaxis_title = "Time",
            yaxis_title=self.ytitle + "(" + self.symbol + ")"
        )

        st.plotly_chart(fig)

    def specific8pm(self):
        """
        Graphing specific outliers from 8:01 pm to 8:03 pm
        """
        spike_end = dt.datetime(2023, 1, 6, 20, 30)
        spike = self.outliers_df[self.outliers_df["datetime"] < spike_end]

        # Smoothening function
        idx = range(len(spike))
        xnew = np.linspace(min(idx), max(idx), 300)
        spl = make_interp_spline(idx, spike[self.col], k=3)
        ynew = spl(xnew)

        # Output plot
        fig = plt.figure()
        sns.lineplot(x=xnew, y=ynew, alpha=0.6, color="r")
        plt.axhline(y=self.avg, color="blue", alpha=0.4, linestyle="--", label="Day Average")
        plt.xticks(idx[::5], spike["datetime"].dt.strftime("%I:%M:%S %p")[::5])
        # Meta data
        # plt.xlabel("Time")
        plt.ylabel(self.ytitle + "(" + self.symbol + ")")
        plt.title("Outliers b/w 8:01 pm - 8:03 pm")
        plt.legend()

        st.pyplot(fig)

    def raw_inlier(self):
        """
        A distribution on inliers
        """
        # Calculate human activity avg
        # above0avg = self.df[s]

        fig = px.scatter(
            data_frame=self.normal_df,
            x = "datetime",
            y=self.col,
            opacity=0.1,
        )

        fig.add_hline(
            y=self.avg,
            line_dash = "dash",
            annotation_text="Average EMF Radiation",
            annotation_position = "top left",
            annotation_font_color = "black"
        )

        if self.safe_level != 0:
            fig.add_hline(
                y = self.safe_level,
                line_dash = "dot",
                line_color = "limegreen",
                annotation_text = "Safe level",
                annotation_position = "top left",
                annotation_font_color = "limegreen"
            )

        fig.update_layout(
            title=self.ytitle + " Points",
            xaxis_title = "Time",
            yaxis_title=self.ytitle + "(" + self.symbol + ")",
        )

        fig.update_traces(
            marker=dict(
                color="blue"
            )
        )

        st.plotly_chart(fig)

    def moving_average(self):
        """
        Plot moving averages graph and get average of zoomed plots
        """
        fig = go.Figure()

        # Add MAs
        fig.add_scatter(
            x = self.normal_df["datetime"].iloc[::10],
            y = self.normal_df["MA60"].iloc[::10],
            name = "1 min average",
            mode = "lines+markers",
        )
        fig.add_scatter(
            x = self.normal_df["datetime"].iloc[::10],
            y = self.normal_df["MA180"].iloc[::10],
            name = "3 min average",
            mode = "lines+markers"
        )
        fig.add_scatter(
            x = self.normal_df["datetime"].iloc[::10],
            y = self.normal_df["MA300"].iloc[::10],
            name = "5 min average",
            mode = "lines+markers"
        )
        if self.safe_level != 0:
            fig.add_hline(
                y = self.safe_level,
                line_dash = "dot",
                line_color = "limegreen",
                annotation_text = "Safe level",
                annotation_position = "top left",
                annotation_font_color = "limegreen"
            )

        # Updates
        fig.update_layout(
            title="Moving Average of " + self.ytitle + " over a day",
            xaxis_title = "Time",
            yaxis_title=self.ytitle + "(" + self.symbol + ")"
        )
        fig.update_traces(
            marker=dict(
                size=2,
                #colorscale="Viridis"
            ),
        )

        # Output chart
        st.plotly_chart(fig)


    """ ------------------ Next page ----------------"""

    def calculate_avg(self):
        """
        Function to calculate average of selected portion in graph
        """
        self.calculate()
        fig = go.Figure()

        # Add traces
        fig.add_scatter(
            x = self.normal_df["datetime"].iloc[::30],
            y = self.normal_df["MA180"].iloc[::30],
            name = "3 min average",
            mode = "lines+markers"
        )
        if self.safe_level != 0:
            fig.add_hline(
                y = self.safe_level,
                line_dash = "dot",
                line_color = "limegreen",
                annotation_text = "Safe level",
                annotation_position = "top left",
                annotation_font_color = "limegreen"
            )

        # Updates
        fig.update_layout(
            {"uirevision" : "foo"},
            title="Moving Average of " + self.ytitle + " over a day",
            xaxis_title = "Time",
            yaxis_title=self.ytitle + "(" + self.symbol + ")",
            overwrite=True
        )
        fig.update_traces(
            marker=dict(
                size=2,
                color="blue"
                #colorscale="Viridis"
            ),
        )

        # Callback
        selected = plotly_events(fig, click_event=False, select_event=True)

        # Average
        col1, col2, col3 = st.columns(3)
        col2.metric(
            label="Average",
            value=f"{self.new_avg(selected):.2f} {self.symbol}"
        )

    def new_avg(self, selected: list):
        """
        Given a list of dictionaries
        """
        total = 0
        if (selected is None) or (len(selected) == 0):
            return 0
        for ele in selected:
            total += ele['y']
        return total/len(selected)



def draw_all(analysis: Analysis):
    title()
    analysis.plot_all()