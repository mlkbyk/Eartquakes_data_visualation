
"""SEISMOSCOPE | Shared Streamlit UI Styles."""

import streamlit as st


def apply_app_style():

    st.markdown(
        """
        <style>

        /* MAIN PAGE */

        .stApp {
            background: #F8FAFC;
            color: #0F172A;
        }

        [data-testid="stSidebar"] {
            background: #F1F5F9;
            border-right: 1px solid #E2E8F0;
        }

        [data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.94);
        }

        .block-container {
            max-width: 1370px;
            padding-top: 4.75rem !important;
            padding-bottom: 2.5rem;
        }


        /* KPI CARDS */

        [data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(15,23,42,.03);
        }

        [data-testid="stMetricLabel"] {
            color: #64748B;
            font-weight: 500;
        }

        [data-testid="stMetricValue"] {
            color: #0F172A;
            font-weight: 700;
        }


        /* PAGE HEADER */

        .eyebrow-badge {
            display: inline-block;
            background: #CCFBF1;
            color: #0F766E;
            font-size: .73rem;
            font-weight: 700;
            letter-spacing: .09em;
            padding: 5px 12px;
            border-radius: 999px;
            margin-bottom: 9px;
        }

        .page-heading {
            color: #0F172A;
            font-size: 2rem;
            font-weight: 750;
            margin: .2rem 0;
        }

        .page-caption {
            color: #475569;
            font-size: .95rem;
            margin-bottom: 1.1rem;
        }


        /* SCIENTIFIC INSIGHT CARD */

        .insight-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-left: 4px solid #0F766E;
            border-radius: 12px;
            padding: 18px;
            color: #334155;
            font-size: .91rem;
            line-height: 1.65;
            box-shadow: 0 1px 3px rgba(15,23,42,.03);
        }

        .insight-card h4 {
            color: #0F172A;
            font-size: 1rem;
            margin: 0 0 12px;
        }

        .insight-note {
            border-top: 1px solid #E2E8F0;
            margin-top: 14px;
            padding-top: 12px;
            color: #475569;
            font-size: .84rem;
        }


        /* CHART AND TABLE CARDS */

        div[class*="st-key-chart_card_"] {
            background: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 1px 3px rgba(15,23,42,.03);
        }


        /* TABS */

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #0F766E !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
