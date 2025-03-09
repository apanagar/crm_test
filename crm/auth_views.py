from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
import logging
import traceback

logger = logging.getLogger('crm.auth_views')

class DebugLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        logger.debug('Request Method: %s', request.method)
        logger.debug('Request POST data keys: %s', list(request.POST.keys()))
        logger.debug('Request GET data: %s', request.GET)
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error('Exception in dispatch: %s', str(e))
            logger.error('Traceback: %s', traceback.format_exc())
            raise

    def form_valid(self, form):
        logger.info('Login attempt for user: %s', form.get_user())
        logger.debug('Form data: %s', form.cleaned_data)
        try:
            return super().form_valid(form)
        except Exception as e:
            logger.error('Exception in form_valid: %s', str(e))
            logger.error('Traceback: %s', traceback.format_exc())
            raise

    def form_invalid(self, form):
        logger.warning('Invalid login attempt')
        logger.warning('Form errors: %s', form.errors)
        logger.debug('Form data: %s', form.data)
        try:
            return super().form_invalid(form)
        except Exception as e:
            logger.error('Exception in form_invalid: %s', str(e))
            logger.error('Traceback: %s', traceback.format_exc())
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            logger.info('Context data keys: %s', list(context.keys()))
            return context
        except Exception as e:
            logger.error('Exception in get_context_data: %s', str(e))
            logger.error('Traceback: %s', traceback.format_exc())
            raise 