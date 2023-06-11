import sqlite3
from tika import parser
import spacy
import streamlit as st
import pandas as pd
import base64
import random
import time
import datetime
import nltk
from nltk.corpus import stopwords
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter

import io
import random
from streamlit_tags import st_tags
from PIL import Image
#import pymysql
import pafy
import plotly.express as px


def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(csv.encode()).decode()
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(
        resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


connection = sqlite3.connect('resume_parser.db')
cursor = connection.cursor()


def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    print("it came hereeeeeeeeeeeeeeeeeeeeeeeee", name)
    resume_data2 = (name, email, str(res_score), timestamp, int(
        no_of_pages), reco_field, cand_level, skills, recommended_skills, courses)

    print("main data here ", resume_data2)

    cursor.execute(''' INSERT INTO user_data(Name, Email_ID, resume_score ,Timestamp,Page_no,Predicted_Field,User_Level, Actual_skills,Recommended_skills,Recommended_courses)
            VALUES(?,?,?,?,?,?,?,?,?,?)''', resume_data2)

    connection.commit()
    # connection.close()


st.set_page_config(
    page_title="Job Candidature Analysis",
    page_icon='./Logo/LOGO.png',
)


def run():
    st.title("Job Candidature Analysis")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox(
        "Choose among the given options:", activities)
    img = Image.open('./Logo/skills.png')
    # img = img.resize((250,250))
    st.image(img)

    # cursor.execute(table_sql)
    if choice == 'Normal User':
        # st.markdown('''<h4 style='text-align: left; color: #d73b5c;'> Upload your resume to get smart recommendation based on it. </h4>''',
        # unsafe_allow_html=True)

        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            # with st.spinner('Uploading your Resume....'):
            #     time.sleep(4)
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            print("first it comes here ", resume_data)
            if resume_data:
                # Get the whole resume data
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown(
                        '''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown(
                        '''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''', unsafe_allow_html=True)

                # Skill shows
                keywords = st_tags(label='### Skills that you have',
                                   text='See our skills recommendation',
                                   value=resume_data['skills'], key='1')

                # recommendation
                ds_keyword = ['tensorflow', 'keras', 'pytorch',
                              'machine learning', 'deep Learning', 'flask', 'streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = [
                    'android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development',
                               'swift', 'cocoa', 'cocoa touch', 'xcode']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                                'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience']

                recommended_skills = []

                # Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(
                    ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(
                    ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)

                # Personality
                # st.subheader("**Soft Skills🧠**")

                # time_mgmt = ['administered', 'analyzed', 'appointed', 'approved', 'assigned', 'attained', 'authorized', 'chaired', 'considered', 'consolidated', 'contracted', 'controlled', 'converted', 'coordinated', 'decided', 'delegated', 'developed', 'directed', 'eliminated', 'emphasized', 'enforced', 'enhanced', 'established', 'executed', 'generated', 'handled', 'headed', 'hired',
                #  'hosted', 'improved', 'incorporated', 'increased', 'initiated', 'inspected', 'instituted', 'led', 'managed', 'merged', 'motivated', 'organized', 'originated', 'overhauled', 'oversaw', 'planned', 'presided', 'prioritized', 'produced', 'recommended', 'reorganized', 'replaced', 'restored', 'reviewed', 'scheduled', 'streamlined', 'strengthened', 'simultaneously', 'prioritised']

                # comm_skills = ['addressed', 'advertised', 'arbitrated', 'arranged', 'articulated', 'authored', 'clarified', 'collaborated', 'communicated', 'composed', 'condensed', 'conferred', 'consulted', 'contacted', 'conveyed', 'convinced', 'corresponded', 'debated', 'defined', 'described', 'developed', 'directed', 'discussed', 'drafted', 'edited', 'elicited', 'enlisted', 'explained', 'expressed', 'formulated', 'furnished', 'incorporated', 'influenced',
                #    'interacted', 'interpreted', 'interviewed', 'involved', 'joined', 'judged', 'lectured', 'listened', 'marketed', 'mediated', 'moderated', 'negotiated', 'observed', 'outlined', 'participated', 'persuaded', 'presented', 'promoted', 'proposed', 'publicized', 'reconciled', 'recruited', 'referred', 'reinforced', 'reported', 'resolved', 'responded', 'solicited', 'specified', 'spoke', 'suggested', 'summarized', 'synthesized', 'translated', 'wrote']

                # creativity = ['acted', 'adapted', 'began', 'combined', 'conceptualized', 'condensed', 'created', 'customized', 'designed', 'developed', 'directed', 'displayed', 'drew', 'entertained', 'established', 'fashioned', 'formulated',
                #   'founded', 'illustrated', 'initiated', 'instituted', 'integrated', 'introduced', 'invented', 'modeled', 'modified', 'originated', 'performed', 'photographed', 'planned', 'revised', 'revitalized', 'shaped', 'solved']

                # team_work = ['approved', 'arranged', 'cataloged', 'categorized', 'charted', 'classified', 'coded', 'collected', 'compiled', 'corresponded', 'distributed', 'executed', 'filed', 'generated', 'implemented', 'incorporated', 'inspected', 'logged', 'maintained', 'monitored', 'obtained', 'operated', 'ordered', 'organized', 'prepared', 'processed', 'provided', 'purchased', 'recorded', 'registered', 'reserved', 'responded', 'reviewed', 'routed', 'scheduled', 'screened', 'set up', 'submitted', 'supplied', 'standardized',
                #  'systematized', 'updated', 'validated', 'verified', 'adapted', 'advocated', 'aided', 'answered', 'arranged', 'assessed', 'assisted', 'cared for', 'clarified', 'coached', 'collaborated', 'contributed', 'cooperated', 'counseled', 'demonstrated', 'diagnosed', 'educated', 'encouraged', 'ensured', 'expedited', 'facilitated', 'familiarize', 'furthered', 'guided', 'helped', 'insured', 'intervened', 'motivated', 'provided', 'referred', 'rehabilitated', 'presented', 'resolved', 'simplified', 'supplied', 'supported', 'volunteered']

                persona_dict = {'Time Management': ['administered', 'analyzed', 'appointed', 'approved', 'assigned', 'attained', 'authorized', 'chaired', 'considered', 'consolidated', 'contracted', 'controlled', 'converted', 'coordinated', 'decided', 'delegated', 'developed', 'directed', 'eliminated', 'emphasized', 'enforced', 'enhanced', 'established', 'executed', 'generated', 'handled', 'headed', 'hired', 'hosted', 'improved', 'incorporated', 'increased', 'initiated', 'inspected', 'instituted', 'led', 'managed', 'merged', 'motivated', 'organized', 'originated', 'overhauled', 'oversaw', 'planned', 'presided', 'prioritized', 'produced', 'recommended', 'reorganized', 'replaced', 'restored', 'reviewed', 'scheduled', 'streamlined', 'strengthened', 'simultaneously', 'prioritised', 'appointed',    'approved',    'assigned',    'attained',    'authorized',    'chaired',    'considered',    'consolidated',    'contracted',    'controlled',    'converted',    'coordinated',    'decided',    'delegated',    'developed',    'directed',    'eliminated',    'emphasized',    'enforced',    'enhanced',    'established',    'executed',    'generated',    'handled',    'headed',    'hired',    'hosted',    'improved',    'incorporated',    'increased',    'initiated',    'inspected',    'instituted',    'led',    'managed',    'merged',    'motivated',    'organized',    'originated',    'overhauled',    'oversaw',    'planned',    'presided',    'prioritized',    'produced',    'recommended',    'reorganized',    'replaced',    'restored',    'reviewed',    'scheduled',    'streamlined',    'strengthened',    'simultaneously',    'prioritised',    'efficient',    'punctual',    'timely',    'systematic',    'organized',    'disciplined',    'structured',    'methodical',    'proactive',    'productive',    'synchronized',    'coordinated',    'controlled',    'deadline_oriented',    'task_oriented',    'detail_oriented',    'resourceful',    'self_disciplined',    'goal_oriented',    'time_conscious',    'multi_tasking',    'prioritizing',    'streamlining',    'optimizing',    'time_sensitive',    'adhering_to_schedules',    'meeting_deadlines',    'planning_ahead',    'allocating_resources',    'tracking_progress',    'time_allocation',    'task_management',    'schedule_management',    'workload_management',    'effective_planning',    'time_optimization',    'time_tracking',    'time_utilization',    'meeting_timeframes',    'time_efficiency',    'time_effectiveness',    'time_consciousness'],

                                'Communication Skills': ['addressed',
                                                         'advertised',
                                                         'arbitrated',
                                                         'arranged',
                                                         'articulated',
                                                         'authored',
                                                         'clarified',
                                                         'collaborated',
                                                         'communicated',
                                                         'composed',
                                                         'condensed',
                                                         'conferred',
                                                         'consulted',
                                                         'contacted',
                                                         'conveyed',
                                                         'convinced',
                                                         'corresponded',
                                                         'debated',
                                                         'defined',
                                                         'described',
                                                         'developed',
                                                         'directed',
                                                         'discussed',
                                                         'drafted',
                                                         'edited',
                                                         'elicited',
                                                         'enlisted',
                                                         'explained',
                                                         'expressed',
                                                         'formulated',
                                                         'furnished',
                                                         'incorporated',
                                                         'influenced',
                                                         'interacted',
                                                         'interpreted',
                                                         'interviewed',
                                                         'involved',
                                                         'joined',
                                                         'judged',
                                                         'lectured',
                                                         'listened',
                                                         'marketed',
                                                         'mediated',
                                                         'moderated',
                                                         'negotiated',
                                                         'observed',
                                                         'outlined',
                                                         'participated',
                                                         'persuaded',
                                                         'presented',
                                                         'promoted',
                                                         'proposed',
                                                         'publicized',
                                                         'reconciled',
                                                         'recruited',
                                                         'referred',
                                                         'reinforced',
                                                         'reported',
                                                         'resolved',
                                                         'responded',
                                                         'solicited',
                                                         'specified',
                                                         'spoke',
                                                         'suggested',
                                                         'summarized',
                                                         'synthesized',
                                                         'translated',
                                                         'wrote',
                                                         'listened',
                                                         'empathized',
                                                         'persuasive',
                                                         'concise',
                                                         'engaging',
                                                         'diplomatic',
                                                         'negotiation',
                                                         'influential',
                                                         'interpersonal',
                                                         'oral',
                                                         'written',
                                                         'presentation',
                                                         'active_listening',
                                                         'nonverbal_communication',
                                                         'feedback',
                                                         'collaboration',
                                                         'intercultural_communication',
                                                         'teamwork',
                                                         'verbal_communication',
                                                         'professionalism',
                                                         'public_speaking',
                                                         'questioning',
                                                         'relationship_building',
                                                         'storytelling',
                                                         'conflict_resolution',
                                                         'clarity',
                                                         'flexibility',
                                                         'assertiveness',
                                                         'open-mindedness',
                                                         'empathy',
                                                         'patience',
                                                         'cultural_sensitivity',
                                                         'tactfulness',
                                                         'adaptability',
                                                         'diplomacy',
                                                         'listening_comprehension',
                                                         'interpretation',
                                                         'persuasion',
                                                         'negotiation_skills',
                                                         'communication_strategy',
                                                         'communication_effectiveness',
                                                         'communication_styles',
                                                         'information_exchange',
                                                         'collaborative_skills',
                                                         'constructive_feedback',
                                                         'professional_correspondence',
                                                         'verbal_expression',
                                                         'written_expression'],

                                'Research skills': ['analyzed',
                                                    'clarified',
                                                    'collected',
                                                    'compared',
                                                    'conducted',
                                                    'critiqued',
                                                    'detected',
                                                    'determined',
                                                    'diagnosed',
                                                    'evaluated',
                                                    'examined',
                                                    'experimented',
                                                    'explored',
                                                    'extracted',
                                                    'formulated',
                                                    'gathered',
                                                    'identified',
                                                    'inspected',
                                                    'interpreted',
                                                    'interviewed',
                                                    'invented',
                                                    'investigated',
                                                    'located',
                                                    'measured',
                                                    'organized',
                                                    'researched',
                                                    'searched',
                                                    'solved',
                                                    'summarized',
                                                    'surveyed',
                                                    'systematized',
                                                    'tested',
                                                    'synthesized',
                                                    'validated',
                                                    'verified',
                                                    'assessed',
                                                    'scrutinized',
                                                    'probed',
                                                    'discovered',
                                                    'propositioned',
                                                    'examined',
                                                    'scrutinized',
                                                    'cataloged',
                                                    'observed',
                                                    'identified',
                                                    'documented',
                                                    'reviewed',
                                                    'investigated',
                                                    'monitored',
                                                    'analytical',
                                                    'data_analysis',
                                                    'experimentation',
                                                    'critical_thinking',
                                                    'problem_solving',
                                                    'information_gathering',
                                                    'information_synthesis',
                                                    'literature_review',
                                                    'research_methodology',
                                                    'statistical_analysis',
                                                    'quantitative_research',
                                                    'qualitative_research',
                                                    'data_collection',
                                                    'data_interpretation',
                                                    'data_processing',
                                                    'data_validation',
                                                    'experimental_design',
                                                    'data_reporting',
                                                    'data_visualization',
                                                    'hypothesis_testing',
                                                    'literature_search',
                                                    'subject_matter_expertise',
                                                    'experimental_techniques',
                                                    'research_planning',
                                                    'data_management',
                                                    'research_ethics',
                                                    'literature_analysis',
                                                    'knowledge_curation',
                                                    'research_proposal',
                                                    'research_techniques',
                                                    'research_findings',
                                                    'research_report',
                                                    'problem_formulation',
                                                    'research_evaluation',
                                                    'information_evaluation',
                                                    'research_strategy',
                                                    'information_management',
                                                    'research_accuracy',
                                                    'research_compliance',
                                                    'research_tools',
                                                    'research_sources',
                                                    'research_authority',
                                                    'experimental_controls',
                                                    'research_contributions',
                                                    'research_publications'],

                                'Technical skills': ['adapted',
                                                     'assembled',
                                                     'built',
                                                     'calculated',
                                                     'computed',
                                                     'conserved',
                                                     'constructed',
                                                     'converted',
                                                     'debugged',
                                                     'designed',
                                                     'determined',
                                                     'developed',
                                                     'engineered',
                                                     'fabricated',
                                                     'fortified',
                                                     'installed',
                                                     'maintained',
                                                     'operated',
                                                     'overhauled',
                                                     'printed',
                                                     'programmed',
                                                     'rectified',
                                                     'regulated',
                                                     'remodeled',
                                                     'repaired',
                                                     'replaced',
                                                     'restored',
                                                     'solved',
                                                     'specialized',
                                                     'standardized',
                                                     'studied',
                                                     'upgraded',
                                                     'utilized',
                                                     'analytical',
                                                     'problem-solving',
                                                     'technical_analysis',
                                                     'troubleshooting',
                                                     'testing',
                                                     'hardware',
                                                     'software',
                                                     'networking',
                                                     'coding',
                                                     'programming',
                                                     'database_management',
                                                     'system_administration',
                                                     'data_structures',
                                                     'algorithms',
                                                     'debugging',
                                                     'technical_documentation',
                                                     'technical_support',
                                                     'technical_training',
                                                     'technical_writing',
                                                     'technical_communication',
                                                     'system_integration',
                                                     'automation',
                                                     'configuration',
                                                     'optimization',
                                                     'simulation',
                                                     'virtualization',
                                                     'cybersecurity',
                                                     'cloud_computing',
                                                     'web_development',
                                                     'mobile_development',
                                                     'data_analysis',
                                                     'data_visualization',
                                                     'data_processing',
                                                     'data_mining',
                                                     'data_management',
                                                     'data_modeling',
                                                     'data_security',
                                                     'data_storage',
                                                     'data_backup',
                                                     'data_recovery',
                                                     'machine_learning',
                                                     'artificial_intelligence',
                                                     'internet_of_things',
                                                     'robotics',
                                                     'electronics',
                                                     'circuit_design',
                                                     'embedded_systems',
                                                     'control_systems',
                                                     'operating_systems',
                                                     'database_design',
                                                     'network_security',
                                                     'network_architecture',
                                                     'server_administration',
                                                     'software_testing',
                                                     'version_control',
                                                     'web_design',
                                                     'user_interface_design',
                                                     'user_experience_design',
                                                     'agile_methodology',
                                                     'project_management',
                                                     'problem_analysis',
                                                     'technical_evaluations',
                                                     'software_deployment',
                                                     'technical_architecture',
                                                     'hardware_design',
                                                     'system_design',
                                                     'system_analysis',
                                                     'system_testing',
                                                     'system_security',
                                                     'scripting',
                                                     'shell_scripting',
                                                     'automation_tools',
                                                     'web_servers',
                                                     'databases',
                                                     'programming_languages',
                                                     'frameworks',
                                                     'operating_systems',
                                                     'debugging_tools',
                                                     'networking_protocols',
                                                     'virtualization_technologies',
                                                     'data_analysis_tools',
                                                     'data_visualization_tools',
                                                     'software_integration',
                                                     'system_configuration',
                                                     'system_optimization',
                                                     'system_simulation',
                                                     'cybersecurity_tools',
                                                     'cloud_platforms',
                                                     'web_frameworks',
                                                     'mobile_frameworks',
                                                     'algorithm_design',
                                                     'algorithm_analysis',
                                                     'coding_languages',
                                                     'database_management_systems',
                                                     'system_administration_tools',
                                                     'networking_tools',
                                                     'software_testing_tools',
                                                     'web_design_tools',
                                                     'agile_tools',
                                                     'project_management_tools',
                                                     'data_security_tools',
                                                     'machine_learning_tools',
                                                     'artificial_intelligence_tools',
                                                     'robotics_tools',
                                                     'electronics_tools',
                                                     'control_systems_tools',
                                                     'operating_systems_tools',
                                                     'database_design_tools',
                                                     'network_security_tools',
                                                     'server_administration_tools',
                                                     'version_control_tools'],

                                'Teaching skills': ['adapted',
                                                    'advised',
                                                    'clarified',
                                                    'coached',
                                                    'communicated',
                                                    'conducted',
                                                    'coordinated',
                                                    'critiqued',
                                                    'developed',
                                                    'enabled',
                                                    'encouraged',
                                                    'evaluated',
                                                    'explained',
                                                    'facilitated',
                                                    'focused',
                                                    'guided',
                                                    'individualized',
                                                    'informed',
                                                    'instilled',
                                                    'instructed',
                                                    'motivated',
                                                    'persuaded',
                                                    'set_goals',
                                                    'simulated',
                                                    'stimulated',
                                                    'taught',
                                                    'tested',
                                                    'trained',
                                                    'transmitted',
                                                    'tutored',
                                                    'lesson_planning',
                                                    'curriculum_design',
                                                    'classroom_management',
                                                    'student_assessment',
                                                    'learning_objectives',
                                                    'educational_resources',
                                                    'pedagogical_approaches',
                                                    'learner-centered',
                                                    'active_learning',
                                                    'differentiated_instruction',
                                                    'student_engagement',
                                                    'problem-based_learning',
                                                    'project-based_learning',
                                                    'peer_collaboration',
                                                    'educational_technology',
                                                    'instructional_design',
                                                    'formative_assessment',
                                                    'summative_assessment',
                                                    'feedback_provision',
                                                    'classroom_discipline',
                                                    'classroom_environment',
                                                    'individualized_instruction',
                                                    'scaffolding',
                                                    'motivational_strategies',
                                                    'student_progress',
                                                    'learning_outcomes',
                                                    'student_motivation',
                                                    'classroom_interactions',
                                                    'knowledge_transfer',
                                                    'facilitation_skills',
                                                    'classroom_communication',
                                                    'active_listening',
                                                    'questioning_techniques',
                                                    'classroom_presentations',
                                                    'educational_materials',
                                                    'educational_psychology',
                                                    'instructional_technology',
                                                    'learning_styles',
                                                    'student_feedback',
                                                    'collaborative_learning',
                                                    'reflection',
                                                    'student_mentoring',
                                                    'classroom_assessment',
                                                    'classroom_participation',
                                                    'student_evaluation',
                                                    'learning_assessment',
                                                    'student_achievement',
                                                    'classroom_innovation',
                                                    'classroom_engagement',
                                                    'classroom_inclusion',
                                                    'cultural_sensitivity',
                                                    'problem_solving',
                                                    'critical_thinking',
                                                    'creative_thinking',
                                                    'analytical_skills',
                                                    'knowledge_integration',
                                                    'curriculum_integration',
                                                    'classroom_adaptation',
                                                    'student_success',
                                                    'classroom_support',
                                                    'educational_goals',
                                                    'collaborative_skills',
                                                    'student_development',
                                                    'student_mentoring',
                                                    'curriculum_alignment',
                                                    'classroom_equity',
                                                    'student_empowerment'],

                                'Financial/Data skills': ['administered',
                                                          'adjusted',
                                                          'allocated',
                                                          'analyzed',
                                                          'appraised',
                                                          'assessed',
                                                          'audited',
                                                          'balanced',
                                                          'calculated',
                                                          'computed',
                                                          'conserved',
                                                          'corrected',
                                                          'determined',
                                                          'developed',
                                                          'estimated',
                                                          'forecasted',
                                                          'managed',
                                                          'marketed',
                                                          'measured',
                                                          'planned',
                                                          'programmed',
                                                          'projected',
                                                          'reconciled',
                                                          'reduced',
                                                          'researched',
                                                          'retrieved',
                                                          'financial_analysis',
                                                          'financial_planning',
                                                          'financial_modeling',
                                                          'data_analysis',
                                                          'data_management',
                                                          'data_visualization',
                                                          'financial_reporting',
                                                          'budgeting',
                                                          'forecasting',
                                                          'financial_statement_analysis',
                                                          'risk_management',
                                                          'financial_controls',
                                                          'cost_analysis',
                                                          'investment_analysis',
                                                          'financial_metrics',
                                                          'financial_strategy',
                                                          'data_integration',
                                                          'data_cleansing',
                                                          'data_manipulation',
                                                          'data_mining',
                                                          'data_interpretation',
                                                          'data_wrangling',
                                                          'financial_forecasting',
                                                          'data_reporting',
                                                          'data_modelling',
                                                          'financial_ratios',
                                                          'financial_tracking',
                                                          'data_extraction',
                                                          'financial_systems',
                                                          'financial_planning_and_analysis',
                                                          'data_insights',
                                                          'data_driven_decision_making',
                                                          'financial_performance',
                                                          'financial_controls',
                                                          'financial_management',
                                                          'data_validation',
                                                          'financial_compliance',
                                                          'financial_metrics',
                                                          'data_quality_assurance',
                                                          'financial_operations',
                                                          'data_analytics',
                                                          'financial_strategy',
                                                          'financial_operations',
                                                          'data_profiling',
                                                          'financial_data_analysis',
                                                          'data_visualization',
                                                          'financial_modelling',
                                                          'financial_statement_preparation',
                                                          'data_integration',
                                                          'financial_budgeting',
                                                          'data_architecture',
                                                          'financial_trend_analysis',
                                                          'data_validation',
                                                          'financial_planning_tools',
                                                          'data_security',
                                                          'financial_risk_management',
                                                          'data_processing',
                                                          'financial_forecasting_models',
                                                          'data_audit',
                                                          'financial_decision_making',
                                                          'data_strategy',
                                                          'financial_statement_review',
                                                          'data_insights',
                                                          'financial_systems_analysis',
                                                          'data_cleaning',
                                                          'financial_controls',
                                                          'data_warehousing',
                                                          'financial_data_management'],

                                'Creativity': ['acted', 'adapted', 'began', 'combined', 'conceptualized', 'condensed', 'created', 'customized', 'designed', 'developed', 'directed', 'displayed', 'drew', 'entertained', 'established', 'fashioned', 'formulated', 'founded', 'illustrated', 'initiated', 'instituted', 'integrated', 'introduced', 'invented', 'modeled', 'modified', 'originated', 'performed', 'photographed', 'planned', 'revised', 'revitalized', 'shaped', 'solved', 'brainstormed',
                                               'innovated',
                                               'imagined',
                                               'improvised',
                                               'created_something_new',
                                               'thought_outside_the_box',
                                               'generated_ideas',
                                               'embraced_unconventional_approaches',
                                               'experimented',
                                               'discovered',
                                               'pioneered',
                                               'crafted',
                                               'composed',
                                               'fabricated',
                                               'conceived',
                                               'devised',
                                               'synthesized',
                                               'reimagined',
                                               'transformed',
                                               'reinvented',
                                               'crafted',
                                               'visualized',
                                               'implemented_creative_solutions',
                                               'challenged_conventional_thinking',
                                               'fostered_innovation',
                                               'embraced_originality',
                                               'pushed_boundaries',
                                               'expressed_unique_perspectives',
                                               'combined_ideas',
                                               'explored_new_possibilities',
                                               'broke_new_ground',
                                               'unleashed_creativity',
                                               'played_with_ideas'],

                                'Team Work': ['approved',
                                              'arranged',
                                              'cataloged',
                                              'categorized',
                                              'charted',
                                              'classified',
                                              'coded',
                                              'collected',
                                              'compiled',
                                              'corresponded',
                                              'distributed',
                                              'executed',
                                              'filed',
                                              'generated',
                                              'implemented',
                                              'incorporated',
                                              'inspected',
                                              'logged',
                                              'maintained',
                                              'monitored',
                                              'obtained',
                                              'operated',
                                              'ordered',
                                              'organized',
                                              'prepared',
                                              'processed',
                                              'provided',
                                              'purchased',
                                              'recorded',
                                              'registered',
                                              'reserved',
                                              'responded',
                                              'reviewed',
                                              'routed',
                                              'scheduled',
                                              'screened',
                                              'set up',
                                              'submitted',
                                              'supplied',
                                              'standardized',
                                              'systematized',
                                              'updated',
                                              'validated',
                                              'verified',
                                              'adapted',
                                              'advocated',
                                              'aided',
                                              'answered',
                                              'arranged',
                                              'assessed',
                                              'assisted',
                                              'cared_for',
                                              'clarified',
                                              'coached',
                                              'collaborated',
                                              'contributed',
                                              'cooperated',
                                              'counseled',
                                              'demonstrated',
                                              'diagnosed',
                                              'educated',
                                              'encouraged',
                                              'ensured',
                                              'expedited',
                                              'facilitated',
                                              'familiarized',
                                              'furthered',
                                              'guided',
                                              'helped',
                                              'insured',
                                              'intervened',
                                              'motivated',
                                              'provided',
                                              'referred',
                                              'rehabilitated',
                                              'presented',
                                              'resolved',
                                              'simplified',
                                              'supplied',
                                              'supported',
                                              'volunteered',
                                              'collaborative',
                                              'team-oriented',
                                              'interdependent',
                                              'partnership',
                                              'unity',
                                              'collective',
                                              'joint',
                                              'shared',
                                              'coordinated',
                                              'cohesive',
                                              'group',
                                              'synergy',
                                              'together',
                                              'mutual',
                                              'synchronized',
                                              'assistance',
                                              'harmony',
                                              'engagement',
                                              'collaboration',
                                              'involvement',
                                              'relationship',
                                              'camaraderie',
                                              'communication',
                                              'cooperation',
                                              'connection',
                                              'integration',
                                              'support',
                                              'unity',
                                              'solidarity',
                                              'respect',
                                              'trust',
                                              'reliability',
                                              'dependability',
                                              'accountability',
                                              'flexibility',
                                              'adaptability',
                                              'empathy',
                                              'active_listening',
                                              'conflict_resolution',
                                              'problem-solving',
                                              'team_building',
                                              'negotiation',
                                              'coaching',
                                              'mentoring',
                                              'delegation',
                                              'leadership',
                                              'camaraderie',
                                              'encouragement',
                                              'motivation',
                                              'celebration',
                                              'celebrating_success',
                                              'constructive_feedback',
                                              'consensus_building',
                                              'open_communication',
                                              'shared_goals',
                                              'shared_vision',
                                              'inclusive',
                                              'encouraging_diversity',
                                              'shared_responsibility',
                                              'collaborative_decision-making',
                                              'trust_building',
                                              'inclusive_participation',
                                              'empowerment',
                                              'interpersonal_skills',
                                              'conflict_management',
                                              'positive_attitude',
                                              'synergistic',
                                              'facilitating',
                                              'teamwork']}

                file_data = parser.from_file(save_image_path)
                parsed_text = file_data['content']

                nlp = spacy.load('en_core_web_sm')
                # extracted_text = {}
                # persona_res = []
                nltk.download("stopwords")
                # set of stopwords in eng
                stop_words = set(stopwords.words('english'))
                tokens = parsed_text.split()
                # remove stopwords
                filtered_tokens = [
                    word for word in tokens if not word in stop_words]

                filtered_text = ' '.join(filtered_tokens)
                tk = filtered_text.split()

                persona_res = []
                for key, value in persona_dict.items():
                    for item in tk:
                        if item in value:
                            persona_res.append(key)
                            break

                # for i in persona_res:
                #     st.write(i)

                personality_keywords = st_tags(label='### Soft Skills🧠',
                                               text='Press enter to add more',
                                               value=persona_res)

                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score = resume_score+20

                if 'Declaration' in resume_text:
                    resume_score = resume_score + 20

                if 'Hobbies' or 'Interests' in resume_text:
                    resume_score = resume_score + 20

                if 'Achievements' in resume_text:
                    resume_score = resume_score + 20

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('** Your Resume Writing Score: ' + str(score)+'**')
                st.warning(
                    "** Note: This score is calculated based on the content that you have added in your Resume. **")
                # st.balloons()
                # fx:add to DB
                # print(resume_data['name']," name ", resume_data['email']," name 2 ", str(resume_score), timestamp,
                #               str(resume_data['no_of_pages']), cand_level, str(resume_data['skills']),
                #               str(recommended_skills))

                # insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                #               str(resume_data['no_of_pages']), cand_level, str(resume_data['skills']),
                #               str(recommended_skills))

                connection.commit()
            else:
                st.error('Something went wrong..')
    else:
        # Admin Side
        st.success('Welcome to Admin Side')
        # st.sidebar.subheader('**ID / Password Required!**')

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'admin' and ad_password == 'admin':
                st.success("Welcome Admin")
                # Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's👨‍💻 Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(
                    df, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)
                # Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)

                # Pie chart for predicted field recommendations
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader(
                    "📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(df, values=values, names=labels,
                             title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                # Pie chart for User's👨‍💻 Experienced Level
                labels = plot_data.User_level.unique()
                values = plot_data.User_level.value_counts()
                st.subheader(
                    "📈 ** Pie-Chart for User's👨‍💻 Experienced Level**")
                fig = px.pie(df, values=values, names=labels,
                             title="Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)

            else:
                st.error("Wrong ID & Password Provided")


run()
