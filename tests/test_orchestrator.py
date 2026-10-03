# AI-ASSISTED: Cursor
# PROMPT: Route planner unit tests for RAG vs web vs combined
# ACCEPTED-BY: vignesh

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from agent.orchestrator import InformationRoute, plan_information_route


def test_personal_rag():
    plan = plan_information_route("What is my project location?")
    assert plan.route == InformationRoute.RAG
    assert plan.use_web is False
    assert plan.reason == "personal_knowledge"


def test_weather_web():
    plan = plan_information_route("What is the weather today in Chennai?")
    assert plan.route == InformationRoute.WEB
    assert plan.use_web is True


def test_latest_news_web():
    plan = plan_information_route("What is the latest AI news?")
    assert plan.route == InformationRoute.WEB


def test_force_web():
    plan = plan_information_route("Selenium documentation", force_web=True)
    assert plan.use_web is True


def test_combined_when_personal_and_current():
    plan = plan_information_route("Using my notes, what is today's Nifty price?")
    assert plan.route == InformationRoute.RAG_AND_WEB
    assert plan.use_web is True
