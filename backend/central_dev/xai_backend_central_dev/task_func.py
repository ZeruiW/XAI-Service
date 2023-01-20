from codecarbon import EmissionsTracker


def task_fun_eng_emission_wrapper(task_func, output_dir, task_ticket, publisher_endpoint_url, task_parameters):
    tracker = EmissionsTracker(
        project_name=task_ticket, tracking_mode='process', output_dir=output_dir, log_level='critical')
    tracker.start()
    try:
        status = task_func(
            task_ticket, publisher_endpoint_url, task_parameters)
    except Exception as e:
        raise e
    finally:
        tracker.stop()
    return status
