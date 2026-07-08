# 🇩🇪 AI German A1 Tutor

This project is an interactive AI language tutor designed to help beginners learn German through natural conversations instead of traditional question-and-answer interactions.

Unlike a standard chatbot that simply provides answers, the tutor acts as a real language teacher by encouraging learners to think, make mistakes, and improve through guided practice.

## ✨ Features

- 💬 **German-Only Roleplay**
  - Maintains conversations entirely in German (A1 level).
  - Provides English hints only when the learner gets stuck.

- 📝 **Grammar & Spelling Analysis**
  - Detects grammatical and spelling mistakes.
  - Explains corrections in a beginner-friendly way.
  - Tracks recurring mistakes to personalize future lessons.

- 🧠 **Personalized Learning**
  - Remembers common errors.
  - Reinforces weak vocabulary and grammar topics.

- 🎴 **Interactive Practice Modes**
  - Free-flowing conversational practice.
  - Vocabulary flashcards.
  - Sentence-building exercises.

- ⚡ **LangChain LCEL Architecture**
  - Modular prompt pipelines.
  - Structured output generation.
  - Easily extensible for additional learning modules.

## 🏗️ Architecture

The tutor is built around LangChain Expression Language (LCEL) and separates responsibilities into specialized components:

- Conversation Engine
- Grammar & Error Analyzer
- Student Memory
- Hint Generator
- Flashcard Generator
- Learning Progress Tracker

Together, these components create an adaptive learning experience that behaves more like a real language tutor than a generic AI chatbot.

## 🚀 Goal

The objective of this project is to demonstrate how modern LLM orchestration with LangChain LCEL can be used to build an intelligent, interactive language-learning assistant that adapts to each learner's progress.
